from abc import ABC
from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel, conint
from typing_extensions import TypeAlias

T = TypeVar("T")

GreaterEqualZero: TypeAlias = conint(ge=0)
GreaterEqualOne: TypeAlias = conint(ge=1)


class PageParams(BaseModel):
    page: conint(ge=1)
    size: conint(ge=1, le=100)


class Page(BaseModel, Generic[T], ABC):
    items: Sequence[T]
    page: Optional[GreaterEqualOne]
    pages: Optional[GreaterEqualZero] = None
    size: Optional[GreaterEqualOne]
    total: Optional[GreaterEqualZero]
