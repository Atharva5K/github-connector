from __future__ import annotations

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import ConnectorError
from app.services.oauth_state import OAuthStateStore


def _build_http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        timeout=httpx.Timeout(15.0, connect=5.0),
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.http_client = _build_http_client()
    app.state.oauth_state_store = OAuthStateStore(
        ttl_seconds=settings.oauth_state_ttl_seconds
    )
    try:
        yield
    finally:
        await app.state.http_client.aclose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "A GitHub cloud connector exposing documented REST endpoints for "
        "repository discovery, issue listing, pull request creation, and "
        "optional GitHub OAuth 2.0 authentication."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "GitHub Authentication",
            "description": "OAuth 2.0 login helpers for obtaining a GitHub access token.",
        },
        {
            "name": "GitHub Connector",
            "description": "Documented GitHub repository and collaboration actions.",
        },
    ],
    lifespan=lifespan,
)


@app.exception_handler(ConnectorError)
async def connector_error_handler(_, exc: ConnectorError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(api_router)
