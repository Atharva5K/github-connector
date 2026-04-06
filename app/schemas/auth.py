from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, Field


class OAuthLoginResponse(BaseModel):
    authorization_url: AnyHttpUrl
    state: str = Field(..., description="Single-use CSRF protection token")
    expires_in_seconds: int
    note: str


class OAuthTokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: list[str]
