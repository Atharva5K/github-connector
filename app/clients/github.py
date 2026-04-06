from __future__ import annotations

from typing import Any, Iterable
from urllib.parse import urlencode

import httpx

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, GitHubAPIError
from app.schemas.github import IssueState, OwnerType, PullRequestCreateRequest


class GitHubClient:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        settings: Settings,
        token: str | None,
    ) -> None:
        self._http_client = http_client
        self._settings = settings
        self._token = token

    async def list_repositories(
        self,
        owner: str,
        owner_type: OwnerType,
        page: int,
        per_page: int,
    ) -> list[dict[str, Any]]:
        resource = "users" if owner_type == OwnerType.user else "orgs"
        return await self._request(
            "GET",
            f"https://api.github.com/{resource}/{owner}/repos",
            expected_statuses=(200,),
            params={"page": page, "per_page": per_page},
        )

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: IssueState,
        page: int,
        per_page: int,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            expected_statuses=(200,),
            params={"state": state.value, "page": page, "per_page": per_page},
        )

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        payload: PullRequestCreateRequest,
    ) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            expected_statuses=(201,),
            json=payload.model_dump(),
        )

    def build_authorization_url(self, state: str) -> str:
        self._ensure_oauth_is_configured()
        query = urlencode(
            {
                "client_id": self._settings.github_client_id,
                "redirect_uri": str(self._settings.github_oauth_redirect_uri),
                "scope": self._settings.github_oauth_scope,
                "state": state,
                "allow_signup": "false",
            }
        )
        return f"{self._settings.github_authorize_url}?{query}"

    async def exchange_code_for_access_token(self, code: str) -> dict[str, Any]:
        self._ensure_oauth_is_configured()
        payload = {
            "client_id": self._settings.github_client_id,
            "client_secret": self._settings.github_client_secret.get_secret_value(),
            "code": code,
            "redirect_uri": str(self._settings.github_oauth_redirect_uri),
        }
        data = await self._request(
            "POST",
            str(self._settings.github_token_url),
            expected_statuses=(200,),
            headers={"Accept": "application/json"},
            data=payload,
            include_auth=False,
        )
        if "error" in data:
            message = data.get("error_description") or data.get("error")
            raise AuthenticationError(message=message)
        return data

    async def _request(
        self,
        method: str,
        url: str,
        expected_statuses: Iterable[int],
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        include_auth: bool = True,
    ) -> Any:
        request_headers = dict(headers or {})
        if include_auth and self._token:
            request_headers["Authorization"] = f"Bearer {self._token}"

        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=request_headers,
            )
        except httpx.TimeoutException as exc:
            raise GitHubAPIError(
                status_code=504,
                message="GitHub did not respond before the connector timed out.",
            ) from exc
        except httpx.HTTPError as exc:
            raise GitHubAPIError(
                status_code=502,
                message="The connector could not reach GitHub.",
            ) from exc

        if response.status_code not in expected_statuses:
            raise GitHubAPIError(
                status_code=response.status_code,
                message=self._extract_error_message(response),
            )

        if not response.content:
            return {}

        return response.json()

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

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            return f"GitHub returned HTTP {response.status_code}."

        message = payload.get("message", "GitHub returned an error.")
        errors = payload.get("errors")
        if isinstance(errors, list) and errors:
            first_error = errors[0]
            if isinstance(first_error, dict):
                detail = first_error.get("message") or first_error.get("code")
                if detail:
                    return f"{message} ({detail})"
        return message
