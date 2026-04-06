from __future__ import annotations

import asyncio

import pytest

from app.schemas.github import IssueState, PullRequestCreateRequest
from app.services.github_connector import GitHubConnectorService


class FakeGitHubClient:
    async def list_issues(self, owner, repo, state, page, per_page):
        return [
            {
                "id": 1,
                "number": 12,
                "title": "Actual issue",
                "state": "open",
                "html_url": "https://github.com/acme/project/issues/12",
                "created_at": "2026-04-06T10:00:00Z",
                "updated_at": "2026-04-06T10:00:00Z",
                "user": {"login": "octocat"},
                "assignees": [{"login": "maintainer"}],
                "labels": [{"name": "bug"}],
            },
            {
                "id": 2,
                "number": 13,
                "title": "Pull request masquerading as issue",
                "state": "open",
                "html_url": "https://github.com/acme/project/pull/13",
                "created_at": "2026-04-06T10:00:00Z",
                "updated_at": "2026-04-06T10:00:00Z",
                "user": {"login": "octocat"},
                "assignees": [],
                "labels": [],
                "pull_request": {"url": "https://api.github.com/repos/acme/project/pulls/13"},
            },
        ]


def test_list_issues_filters_pull_requests():
    service = GitHubConnectorService(FakeGitHubClient())

    issues = asyncio.run(
        service.list_issues(
            owner="acme",
            repo="project",
            state=IssueState.open,
            page=1,
            per_page=30,
        )
    )

    assert len(issues) == 1
    assert issues[0].number == 12


def test_pull_request_payload_rejects_same_head_and_base():
    with pytest.raises(ValueError):
        PullRequestCreateRequest(
            title="Invalid PR",
            head="main",
            base="main",
        )
