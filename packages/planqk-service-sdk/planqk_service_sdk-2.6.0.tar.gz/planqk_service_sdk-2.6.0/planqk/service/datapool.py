import typing
from enum import Enum

import pydantic

from .sdk.core.pydantic_utilities import IS_PYDANTIC_V2, UniversalBaseModel


class ReferenceType(str, Enum):
    DATAPOOL = "DATAPOOL"


class DataPoolReference(UniversalBaseModel):
    id: str
    ref: ReferenceType = ReferenceType.DATAPOOL

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(extra="allow",
                                                                                 frozen=True)  # type: ignore # Pydantic v2
    else:
        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
