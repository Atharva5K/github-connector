from __future__ import annotations

from app.clients.github import GitHubClient
from app.schemas.github import (
    IssueState,
    IssueSummary,
    OwnerType,
    PullRequestCreateRequest,
    PullRequestSummary,
    RepositorySummary,
)


class GitHubConnectorService:
    def __init__(self, github_client: GitHubClient) -> None:
        self._github_client = github_client

    async def list_repositories(
        self,
        owner: str,
        owner_type: OwnerType,
        page: int,
        per_page: int,
    ) -> list[RepositorySummary]:
        repositories = await self._github_client.list_repositories(
            owner=owner, owner_type=owner_type, page=page, per_page=per_page
        )
        return [
            RepositorySummary(
                id=repo["id"],
                name=repo["name"],
                full_name=repo["full_name"],
                private=repo["private"],
                description=repo.get("description"),
                html_url=repo["html_url"],
                default_branch=repo["default_branch"],
                visibility=repo.get("visibility"),
                owner_login=repo["owner"]["login"],
            )
            for repo in repositories
        ]

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: IssueState,
        page: int,
        per_page: int,
    ) -> list[IssueSummary]:
        issues = await self._github_client.list_issues(
            owner=owner, repo=repo, state=state, page=page, per_page=per_page
        )
        return [
            IssueSummary(
                id=issue["id"],
                number=issue["number"],
                title=issue["title"],
                state=issue["state"],
                html_url=issue["html_url"],
                created_at=issue["created_at"],
                updated_at=issue["updated_at"],
                user_login=issue["user"]["login"],
                assignees=[assignee["login"] for assignee in issue.get("assignees", [])],
                labels=[label["name"] for label in issue.get("labels", [])],
            )
            for issue in issues
            if "pull_request" not in issue
        ]

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        payload: PullRequestCreateRequest,
    ) -> PullRequestSummary:
        pull_request = await self._github_client.create_pull_request(
            owner=owner, repo=repo, payload=payload
        )
        return PullRequestSummary(
            id=pull_request["id"],
            number=pull_request["number"],
            title=pull_request["title"],
            state=pull_request["state"],
            draft=pull_request["draft"],
            html_url=pull_request["html_url"],
            created_at=pull_request["created_at"],
            head_ref=pull_request["head"]["ref"],
            base_ref=pull_request["base"]["ref"],
            user_login=pull_request["user"]["login"],
        )
