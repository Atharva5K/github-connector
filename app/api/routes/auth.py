from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.dependencies import (
    get_oauth_state_store,
    get_settings_dependency,
    get_unauthenticated_github_client,
)
from app.clients.github import GitHubClient
from app.core.config import Settings
from app.schemas.auth import OAuthLoginResponse, OAuthTokenResponse
from app.services.github_oauth import GitHubOAuthService
from app.services.oauth_state import OAuthStateStore

router = APIRouter(prefix="/auth/github", tags=["GitHub Authentication"])


@router.get(
    "/login",
    response_model=OAuthLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate the GitHub OAuth authorization URL",
)
async def github_login(
    github_client: Annotated[GitHubClient, Depends(get_unauthenticated_github_client)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    state_store: Annotated[OAuthStateStore, Depends(get_oauth_state_store)],
) -> OAuthLoginResponse:
    service = GitHubOAuthService(
        github_client=github_client, settings=settings, state_store=state_store
    )
    return service.build_login_response()


@router.get(
    "/callback",
    response_model=OAuthTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange the GitHub OAuth code for an access token",
    include_in_schema=False,
)
async def github_callback(
    response: Response,
    code: Annotated[str, Query(min_length=1, description="OAuth code from GitHub")],
    state: Annotated[str, Query(min_length=1, description="State returned by login")],
    github_client: Annotated[GitHubClient, Depends(get_unauthenticated_github_client)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
    state_store: Annotated[OAuthStateStore, Depends(get_oauth_state_store)],
) -> OAuthTokenResponse:
    response.headers["Cache-Control"] = "no-store"
    service = GitHubOAuthService(
        github_client=github_client, settings=settings, state_store=state_store
    )
    return await service.exchange_code_for_token(code=code, state=state)
