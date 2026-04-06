from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from app.api.dependencies import get_github_client
from app.clients.github import GitHubClient
from app.schemas.github import (
    IssueState,
    IssueSummary,
    OwnerType,
    PullRequestCreateRequest,
    PullRequestSummary,
    RepositorySummary,
)
from app.services.github_connector import GitHubConnectorService

router = APIRouter(prefix="/github", tags=["GitHub Connector"])


@router.get(
    "/repositories",
    response_model=list[RepositorySummary],
    status_code=status.HTTP_200_OK,
    summary="Fetch repositories for a GitHub user or organization",
)
async def list_repositories(
    owner: Annotated[
        str, Query(min_length=1, description="GitHub username or organization name")
    ],
    github_client: Annotated[GitHubClient, Depends(get_github_client)],
    owner_type: Annotated[
        OwnerType, Query(description="Whether the owner is a user or organization")
    ] = OwnerType.user,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 30,
) -> list[RepositorySummary]:
    service = GitHubConnectorService(github_client)
    return await service.list_repositories(
        owner=owner, owner_type=owner_type, page=page, per_page=per_page
    )


@router.get(
    "/repositories/{owner}/{repo}/issues",
    response_model=list[IssueSummary],
    status_code=status.HTTP_200_OK,
    summary="List issues from a repository",
)
async def list_repository_issues(
    owner: Annotated[str, Path(min_length=1, description="Repository owner")],
    repo: Annotated[str, Path(min_length=1, description="Repository name")],
    github_client: Annotated[GitHubClient, Depends(get_github_client)],
    state: Annotated[
        IssueState, Query(description="Issue state filter")
    ] = IssueState.open,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 30,
) -> list[IssueSummary]:
    service = GitHubConnectorService(github_client)
    return await service.list_issues(
        owner=owner, repo=repo, state=state, page=page, per_page=per_page
    )


@router.post(
    "/repositories/{owner}/{repo}/pull-requests",
    response_model=PullRequestSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Create a pull request",
)
async def create_pull_request(
    owner: Annotated[str, Path(min_length=1, description="Repository owner")],
    repo: Annotated[str, Path(min_length=1, description="Repository name")],
    payload: PullRequestCreateRequest,
    github_client: Annotated[GitHubClient, Depends(get_github_client)],
) -> PullRequestSummary:
    service = GitHubConnectorService(github_client)
    return await service.create_pull_request(owner=owner, repo=repo, payload=payload)
