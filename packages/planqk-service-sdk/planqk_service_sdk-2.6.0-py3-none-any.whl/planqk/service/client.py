import os
import random
import string
import time
import typing

from planqk.service.auth import DEFAULT_TOKEN_ENDPOINT, PlanqkServiceAuth
from planqk.service.sdk import PlanqkServiceApi, ServiceExecution, GetResultResponse
from planqk.service.sdk.service_api.client import ServiceApiClient
from planqk.service.sdk.types.service_execution_status import ServiceExecutionStatus


class PlanqkServiceExecution:
    def __init__(self, client: "PlanqkServiceClient", service_execution: ServiceExecution):
        self._client = client
        self._service_execution = service_execution

    @property
    def id(self) -> str:
        return self._service_execution.id

    @property
    def status(self) -> ServiceExecutionStatus:
        return self._service_execution.status

    @property
    def created_at(self) -> str:
        return self._service_execution.created_at

    @property
    def started_at(self) -> typing.Optional[str]:
        return self._service_execution.started_at

    @property
    def ended_at(self) -> typing.Optional[str]:
        return self._service_execution.ended_at

    @property
    def has_finished(self) -> bool:
        self.refresh()
        return self.status in ["SUCCEEDED", "FAILED", "CANCELLED"]

    def wait_for_final_state(self, timeout: typing.Optional[float] = None, wait: float = 5) -> None:
        """
        Poll the status until it progresses to a final state.

        Parameters:
            - timeout: Seconds to wait for the job. If ``None``, wait indefinitely.
            - wait: Seconds between queries.

        Raises:
            Exception: If the service execution does not reach a final state before the specified timeout.
        """
        start_time = time.time()
        while not self.has_finished:
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                raise TimeoutError(f"Timeout while waiting for service execution '{self.id}'.")
            time.sleep(wait)

    def refresh(self):
        self._service_execution = self._client.api.get_status(id=self.id)

    def result(self) -> GetResultResponse:
        self.wait_for_final_state()
        delay = 1  # Start with a small delay
        max_delay = 16  # Maximum delay
        while True:
            try:
                result = self._client.api.get_result(id=self.id)
                break  # If the operation succeeds, break out of the loop
            except Exception as e:
                time.sleep(delay)  # If the operation fails, wait
                delay *= 2  # Double the delay
                if delay >= max_delay:
                    raise e  # If the delay is too long, raise the exception
        return result

    def result_files(self) -> typing.List[str]:
        file_names = []
        links = self.result().links
        for link in links:
            file_name = link[0]
            if file_name in ["status", "self"]:
                continue
            file_names.append(file_name)
        return file_names

    def result_file_stream(self, file_name: str) -> typing.Iterator[bytes]:
        return self._client.api.get_result_file(id=self.id, file=file_name)

    def download_result_file(self, file_name: str, target_path: str) -> None:
        # check if target path exists and is a directory
        if not os.path.isdir(target_path):
            raise ValueError(f"Target path '{target_path}' does not exist or is not a directory.")

        abs_target_path = os.path.abspath(target_path)
        file_path = os.path.join(abs_target_path, file_name)

        iterator = self.result_file_stream(file_name)
        with open(file_path, "wb") as f:
            for chunk in iterator:
                f.write(chunk)

    def cancel(self) -> None:
        self._client.api.cancel_execution(id=self.id)

    def logs(self) -> typing.List[str]:
        return self._client.api.get_logs(id=self.id)


class PlanqkServiceClient:
    def __init__(
            self,
            service_endpoint: str,
            consumer_key: typing.Union[str, None],
            consumer_secret: typing.Union[str, None],
            token_endpoint: str = DEFAULT_TOKEN_ENDPOINT,
    ):
        self._service_endpoint = service_endpoint
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._token_endpoint = token_endpoint

        if (self._consumer_key is not None) or (self._consumer_secret is not None):
            self._auth = PlanqkServiceAuth(
                consumer_key=self._consumer_key,
                consumer_secret=self._consumer_secret,
                token_endpoint=self._token_endpoint,
            )
            self._api = PlanqkServiceApi(base_url=self._service_endpoint, token=self._auth.get_token)
        else:
            random_token = "".join(
                random.choices(string.ascii_letters + string.digits, k=21)
            )
            self._api = PlanqkServiceApi(base_url=self._service_endpoint, token=random_token)

    @property
    def api(self) -> ServiceApiClient:
        return self._api.service_api

    def run(self, request: typing.Dict[str, typing.Dict[str, typing.Optional[typing.Any]]]) -> PlanqkServiceExecution:
        service_execution = self.api.start_execution(request=request)
        return PlanqkServiceExecution(client=self, service_execution=service_execution)

    def get_service_execution(self, service_execution_id: str) -> PlanqkServiceExecution:
        service_execution = self.api.get_status(id=service_execution_id)
        return PlanqkServiceExecution(client=self, service_execution=service_execution)

    def get_service_executions(self) -> typing.List[PlanqkServiceExecution]:
        service_executions = self.api.get_service_executions()
        return [PlanqkServiceExecution(client=self, service_execution=e) for e in service_executions]
