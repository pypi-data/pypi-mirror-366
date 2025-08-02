from typing import List

import httpx
from pydantic import BaseModel, RedisDsn

from uprock_sdk import GLOBAL_SETTINGS

CLIENT = httpx.AsyncClient(base_url=GLOBAL_SETTINGS.CORE_API_URL)


class TelegramBotRead(BaseModel):
    id: int

    name: str
    slug: str

    token: str
    redis_uri: RedisDsn

    namespace_id: int


async def get(id_: int) -> TelegramBotRead:
    response = await CLIENT.get(f"/v1/internal/telegram_bots/{id_}")
    response.raise_for_status()

    raw_telegram_bot_data = response.json()
    return TelegramBotRead(**raw_telegram_bot_data)


async def list_all() -> List[TelegramBotRead]:
    response = await CLIENT.get("/v1/internal/telegram_bots")
    response.raise_for_status()

    raw_telegram_bots_data = response.json()
    return [TelegramBotRead(**raw_telegram_bot_data) for raw_telegram_bot_data in raw_telegram_bots_data]
