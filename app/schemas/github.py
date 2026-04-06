from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class OwnerType(str, Enum):
    user = "user"
    org = "org"


class IssueState(str, Enum):
    open = "open"
    closed = "closed"
    all = "all"


class RepositorySummary(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    description: str | None = None
    html_url: str
    default_branch: str
    visibility: str | None = None
    owner_login: str


class IssueSummary(BaseModel):
    id: int
    number: int
    title: str
    state: str
    html_url: str
    created_at: datetime
    updated_at: datetime
    user_login: str
    assignees: list[str] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)


class PullRequestCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    head: str = Field(..., min_length=1, description="Name of the branch with changes")
    base: str = Field(..., min_length=1, description="Target branch to merge into")
    body: str | None = None
    draft: bool = False
    maintainer_can_modify: bool = True

    @model_validator(mode="after")
    def validate_branches(self) -> "PullRequestCreateRequest":
        if self.head == self.base:
            raise ValueError("The head branch must be different from the base branch.")
        return self


class PullRequestSummary(BaseModel):
    id: int
    number: int
    title: str
    state: str
    draft: bool
    html_url: str
    created_at: datetime
    head_ref: str
    base_ref: str
    user_login: str
