from __future__ import annotations

from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.clients.github import GitHubClient
from app.core.config import Settings, get_settings
from app.services.oauth_state import OAuthStateStore


github_token_scheme = HTTPBearer(
    auto_error=False,
    bearerFormat="GitHub Token",
    description=(
        "Use a GitHub Personal Access Token or an OAuth access token returned "
        "by the callback endpoint."
    ),
)


def get_settings_dependency() -> Settings:
    return get_settings()


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_oauth_state_store(request: Request) -> OAuthStateStore:
    return request.app.state.oauth_state_store


def get_github_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Security(github_token_scheme)
    ],
) -> str:
    if credentials is None or not credentials.credentials.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A GitHub bearer token is required for this endpoint.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials.strip()


def get_github_client(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    token: Annotated[str, Depends(get_github_token)],
) -> GitHubClient:
    return GitHubClient(http_client=http_client, settings=settings, token=token)


def get_unauthenticated_github_client(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
) -> GitHubClient:
    return GitHubClient(http_client=http_client, settings=settings, token=None)
