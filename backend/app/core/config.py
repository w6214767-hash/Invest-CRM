"""Настройки приложения, загружаемые из переменных окружения."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация CRM и подключаемых внешних сервисов."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    project_name: str = "ИнвестСкан"
    investscan_release_sha: str = "unverified"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./yurzil_crm.db"
    secret_key: str = "локальный-небоевой-секрет-замените-его"
    access_token_expire_minutes: int = 1440
    cors_origins: list[str] | str = "http://localhost:5173,http://localhost:8080"

    avito_client_id: str = ""
    avito_client_secret: str = ""
    app_url: str = "http://localhost:5173"
    shtab_url: str = "https://shtab.ugsdom.ru/#platform"
    oidc_issuer: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_roles_claim: str = "investscan_roles"
    # Optional initial owner-only rollout using the same verified identity as HQ.
    # Leave empty to keep the existing explicit module-role mode.
    oidc_owner_subject: str = ""
    oidc_required_amr: str = "mfa pwd otp"
    session_minutes: int = 60
    investscan_dev_auth: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    hermes_api_url: str = ""
    hermes_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        """Преобразует строку доменов через запятую в список."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    """Возвращает единственный экземпляр настроек приложения."""
    return Settings()


settings = get_settings()
