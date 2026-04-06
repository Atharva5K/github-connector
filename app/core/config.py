from __future__ import annotations

from functools import lru_cache

from pydantic import AnyHttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "GitHub Cloud Connector"
    github_client_id: str | None = None
    github_client_secret: SecretStr | None = None
    github_oauth_redirect_uri: AnyHttpUrl | None = None
    github_authorize_url: AnyHttpUrl = "https://github.com/login/oauth/authorize"
    github_token_url: AnyHttpUrl = "https://github.com/login/oauth/access_token"
    github_oauth_scope: str = "repo read:user"
    oauth_state_ttl_seconds: int = 600


@lru_cache
def get_settings() -> Settings:
    return Settings()
