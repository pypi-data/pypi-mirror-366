import datetime
import json
from typing import List, Dict, Optional

import httpx
from pydantic import BaseModel

from uprock_sdk import GLOBAL_SETTINGS

CLIENT = httpx.AsyncClient(base_url=GLOBAL_SETTINGS.CORE_API_URL)


class BaseMassMessage(BaseModel):
    messages_json: List[Dict]

    send_at: datetime.datetime
    valid_until: Optional[datetime.datetime] = None
    single_channel_only: bool

    filter_json: Optional[Dict] = None


class MassMessageRead(BaseMassMessage):
    id: int


async def create(dto: BaseMassMessage) -> MassMessageRead:
    mass_message_data = json.loads(dto.model_dump_json(exclude_unset=True))

    response = await CLIENT.post("/v1/internal/mass_messages", json=mass_message_data, timeout=None)
    response.raise_for_status()

    raw_mass_message_data = response.json()
    return MassMessageRead(**raw_mass_message_data)
