import time

from authlib.integrations.httpx_client import OAuth2Client

DEFAULT_TOKEN_ENDPOINT = "https://gateway.platform.planqk.de/token"


class PlanqkServiceAuth:
    def __init__(self, consumer_key: str, consumer_secret: str, token_endpoint: str = DEFAULT_TOKEN_ENDPOINT):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._token_endpoint = token_endpoint
        self._token = None
        self._last_token_fetch = None

    def get_token(self) -> str:
        if self._token is None or self._last_token_fetch is None:
            self._refresh_token()

        if time.time() - self._last_token_fetch > self._token["expires_in"]:
            self._refresh_token()

        return self._token["access_token"]

    def _refresh_token(self):
        with OAuth2Client(self._consumer_key, self._consumer_secret) as client:
            token = client.fetch_token(self._token_endpoint, grant_type='client_credentials')

        self._token = token
        self._last_token_fetch = time.time()
