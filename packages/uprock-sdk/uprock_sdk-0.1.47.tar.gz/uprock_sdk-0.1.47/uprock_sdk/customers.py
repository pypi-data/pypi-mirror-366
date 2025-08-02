import datetime
import enum
import json
from dataclasses import dataclass
from typing import List, Optional, Set

import httpx
from pydantic import BaseModel, EmailStr, Field, computed_field, field_validator, model_validator

from uprock_sdk import GLOBAL_SETTINGS
from uprock_sdk.types import Page, PageParams

CLIENT = httpx.AsyncClient(base_url=GLOBAL_SETTINGS.CORE_API_URL)


class BaseCustomer(BaseModel):
    telegram_id: Optional[int] = None
    email: Optional[EmailStr] = None
    email_verified: Optional[bool] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    last_activity_at: Optional[datetime.datetime] = None
    created_at: Optional[datetime.datetime] = None

    labels: Optional[List["BaseLabel"]] = None
    namespaces: Optional[List[int]] = None
    telegram_bots: Optional[List[int]] = None

    @model_validator(mode="after")
    def telegram_id_or_email_or_phone_required(self):
        if not self.telegram_id and not self.email and not self.phone:
            raise ValueError("Either telegram_id or email or phone is required")
        return self

    @field_validator("created_at", "last_activity_at")
    @classmethod
    def dt_is_not_native(cls, v: datetime.datetime) -> datetime.datetime:
        if v and v.tzinfo is None:
            v = v.replace(tzinfo=datetime.timezone.utc)

        return v


class CustomerUpdate(BaseModel):
    telegram_id: Optional[int] = None
    email: Optional[EmailStr] = None
    email_verified: Optional[bool] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    last_activity_at: Optional[datetime.datetime] = None

    @field_validator("last_activity_at")
    @classmethod
    def dt_is_not_native(cls, v: datetime.datetime) -> datetime.datetime:
        if v and v.tzinfo is None:
            v = v.replace(tzinfo=datetime.timezone.utc)

        return v


class CustomerRead(BaseCustomer):
    id: int

    updated_at: datetime.datetime
    created_at: datetime.datetime

    @computed_field
    @property
    def full_name(self) -> str:
        full_name_ = self.first_name

        if full_name_ and self.last_name:
            full_name_ += " "

        if self.last_name:
            if full_name_:
                full_name_ += " "

            full_name_ += self.last_name

        return full_name_

    @computed_field
    @property
    def display_name(self) -> str:
        return self.full_name


@dataclass
class CustomerFilter:
    id__in: Optional[List[int]] = None
    namespace__in: Optional[List[int]] = None
    telegram_bot__in: Optional[List[int]] = None
    search: Optional[str] = None


class BaseLabel(BaseModel):
    name: str
    value: Optional[str] = None

    namespace_id: int = Field(default_factory=lambda: GLOBAL_SETTINGS.NAMESPACE_ID)
    telegram_bot_id: Optional[int] = None


class LabelAssignMode(str, enum.Enum):
    DO_NOTHING_ON_CONFLICT = "DO_NOTHING_ON_CONFLICT"
    REPLACE_ON_CONFLICT = "REPLACE_ON_CONFLICT"


class LabelAssign(BaseModel):
    labels: List[BaseLabel]
    mode: LabelAssignMode = LabelAssignMode.DO_NOTHING_ON_CONFLICT


class LabelUnassign(BaseModel):
    labels: List[BaseLabel]


class TelegramBotAssign(BaseModel):
    telegram_bots: List[int]


async def create(dto: BaseCustomer) -> CustomerRead:
    customer_data = json.loads(dto.model_dump_json(exclude_unset=True))

    if GLOBAL_SETTINGS.NAMESPACE_ID is not None:
        if "namespaces" not in customer_data or not customer_data["namespaces"]:
            customer_data["namespaces"] = [GLOBAL_SETTINGS.NAMESPACE_ID]
        else:
            customer_data["namespaces"].append(GLOBAL_SETTINGS.NAMESPACE_ID)

    response = await CLIENT.post("/v1/internal/customers", json=customer_data, timeout=None)
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def get(customer_id: int) -> CustomerRead:
    response = await CLIENT.get(f"/v1/internal/customers/{customer_id}")
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def update(customer_id: int, dto: CustomerUpdate) -> CustomerRead:
    customer_data = json.loads(dto.model_dump_json(exclude_unset=True))

    response = await CLIENT.patch(f"/v1/internal/customers/{customer_id}", json=customer_data)
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def list_(
    filter_: Optional[CustomerFilter] = None, pagination: Optional[PageParams] = None
) -> Page[CustomerRead]:
    params = {}

    if filter_ is not None:
        if filter_.id__in is not None:
            params["id__in"] = ",".join(list(map(str, filter_.id__in)))

        if filter_.namespace__in is not None:
            params["namespace__in"] = ",".join(list(map(str, filter_.namespace__in)))

        if filter_.telegram_bot__in is not None:
            params["telegram_bot__in"] = ",".join(list(map(str, filter_.telegram_bot__in)))

        if filter_.search is not None:
            params["search"] = filter_.search

    if pagination is not None:
        params = {**params, **pagination.model_dump()}

    response = await CLIENT.get("/v1/internal/customers", params=params)
    response.raise_for_status()

    return Page[CustomerRead](**response.json())


async def list_all(filter_: Optional[CustomerFilter] = None, chunk_size: int = 100) -> List[CustomerRead]:
    customers = []

    customer_page = await list_(filter_=filter_, pagination=PageParams(page=1, size=chunk_size))
    customers = customers + list(customer_page.items)

    for page in range(2, customer_page.pages):
        customer_page = await list_(filter_=filter_, pagination=PageParams(page=page, size=chunk_size))
        customers = customers + list(customer_page.items)

    return customers


async def assign_labels(customer_id: int, labels: List[BaseLabel], replace: bool = False) -> CustomerRead:
    response = await CLIENT.post(
        f"/v1/internal/customers/{customer_id}/assign_labels",
        json=LabelAssign(
            labels=labels,
            mode=LabelAssignMode.REPLACE_ON_CONFLICT if replace else LabelAssignMode.DO_NOTHING_ON_CONFLICT,
        ).model_dump(),
    )
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def unassign_labels(customer_id: int, labels: List[BaseLabel]) -> CustomerRead:
    response = await CLIENT.post(
        f"/v1/internal/customers/{customer_id}/unassign_labels", json=LabelUnassign(labels=labels).model_dump()
    )
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def assign_telegram_bots(customer_id: int, telegram_bots: Set[int]) -> CustomerRead:
    response = await CLIENT.post(
        f"/v1/internal/customers/{customer_id}/telegram_bots",
        json=TelegramBotAssign(
            telegram_bots=list(telegram_bots),
        ).model_dump(),
    )
    response.raise_for_status()

    raw_customer_data = response.json()
    return CustomerRead(**raw_customer_data)


async def unassign_telegram_bot(customer_id: int, telegram_bot_id: int) -> None:
    response = await CLIENT.delete(f"/v1/internal/customers/{customer_id}/telegram_bots/{telegram_bot_id}")
    response.raise_for_status()
