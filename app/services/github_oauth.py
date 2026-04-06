from __future__ import annotations

from app.clients.github import GitHubClient
from app.core.config import Settings
from app.core.exceptions import AuthenticationError
from app.schemas.auth import OAuthLoginResponse, OAuthTokenResponse
from app.services.oauth_state import OAuthStateStore


class GitHubOAuthService:
    def __init__(
        self,
        github_client: GitHubClient,
        settings: Settings,
        state_store: OAuthStateStore,
    ) -> None:
        self._github_client = github_client
        self._settings = settings
        self._state_store = state_store

    def build_login_response(self) -> OAuthLoginResponse:
        self._ensure_oauth_is_configured()
        state = self._state_store.issue_state()
        return OAuthLoginResponse(
            authorization_url=self._github_client.build_authorization_url(state),
            state=state,
            expires_in_seconds=self._settings.oauth_state_ttl_seconds,
            note=(
                "Open the authorization_url in a browser, complete the GitHub "
                "consent flow, and use the callback response token as a bearer token."
            ),
        )

    async def exchange_code_for_token(
        self, code: str, state: str
    ) -> OAuthTokenResponse:
        self._ensure_oauth_is_configured()
        if not self._state_store.validate_and_consume(state):
            raise AuthenticationError(
                message="Invalid or expired OAuth state. Start the login flow again."
            )

        payload = await self._github_client.exchange_code_for_access_token(code=code)
        access_token = payload.get("access_token")
        if not access_token:
            raise AuthenticationError(
                message="GitHub did not return an access token for the provided code."
            )

        raw_scope = payload.get("scope", "")
        scopes = [item for item in raw_scope.split(",") if item]
        return OAuthTokenResponse(
            access_token=access_token,
            token_type=payload.get("token_type", "bearer"),
            scope=scopes,
        )

    def _ensure_oauth_is_configured(self) -> None:
        if (
            not self._settings.github_client_id
            or self._settings.github_client_secret is None
            or self._settings.github_oauth_redirect_uri is None
        ):
            raise AuthenticationError(
                message=(
                    "OAuth is not configured. Set GITHUB_CLIENT_ID, "
                    "GITHUB_CLIENT_SECRET, and GITHUB_OAUTH_REDIRECT_URI."
                )
            )
