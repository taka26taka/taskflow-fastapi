from datetime import date, datetime
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/taskflow.db"
    app_timezone: str = "Asia/Tokyo"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
# Fail early for a misspelled timezone rather than misclassifying deadlines.
timezone = ZoneInfo(settings.app_timezone)


def today() -> date:
    return datetime.now(timezone).date()
