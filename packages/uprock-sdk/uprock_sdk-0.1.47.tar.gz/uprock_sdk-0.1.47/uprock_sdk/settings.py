from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CORE_API_URL: str = "http://localhost"
    TERMS_API_URL: str = "http://localhost"

    NAMESPACE_ID: Optional[int] = None

    TERMS_DEFAULT_LANGUAGE: str = "ru"
    TERMS_TTL_S: int = 60

    def update(self, data: dict) -> "Settings":
        update = self.dict()
        update.update(data)

        for k, v in self.validate(update).dict(exclude_defaults=True).items():
            setattr(self, k, v)
        return self


GLOBAL_SETTINGS = Settings()
