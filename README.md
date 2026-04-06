# GitHub Cloud Connector

A minimal FastAPI-based GitHub connector built for the backend assignment. It provides a documented REST API for GitHub repository and collaboration actions, with secure bearer-token access and optional GitHub OAuth 2.0 support.

## Implemented Requirements

- GitHub authentication via bearer token support
- GitHub OAuth 2.0 flow as a bonus implementation
- Real GitHub API integration for:
  - Fetch repositories for a user or organization
  - List issues from a repository
  - Create a pull request
- Swagger UI and OpenAPI documentation
- Clean separation between API, service, and GitHub client layers

## Tech Stack

- Python
- FastAPI
- HTTPX
- Pydantic Settings

## Project Structure

```text
app/
  api/
    routes/
  clients/
  core/
  schemas/
  services/
tests/
```

## Setup

### 1. Create a virtual environment

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
py -3 -m pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and update the values:

```powershell
Copy-Item .env.example .env
```

OAuth configuration values:

- `GITHUB_CLIENT_ID`
- `GITHUB_CLIENT_SECRET`
- `GITHUB_OAUTH_REDIRECT_URI`

Recommended local redirect URI value:

```env
GITHUB_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/github/callback
```

If you only want to test the protected endpoints in Swagger, the app can still be used with a GitHub Personal Access Token.

## Run the API

For normal usage:

```powershell
py -3 -m uvicorn app.main:app
```

The application will be available at:

- API base: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- ReDoc: `http://localhost:8000/redoc`

## Authentication

### Option 1: Personal Access Token

1. Create a GitHub Personal Access Token with the permissions you need.
2. Open Swagger at `/docs`.
3. Click `Authorize`.
4. Paste the token into the bearer auth dialog.

This is the simplest way to test the connector.

### Option 2: GitHub OAuth 2.0

1. Create a GitHub OAuth App in GitHub Developer Settings.
2. Set the app callback URL to:

```text
http://localhost:8000/api/v1/auth/github/callback
```

3. Set the OAuth environment variables in `.env`.
4. Call `GET /api/v1/auth/github/login`.
5. Open the returned `authorization_url` in the browser.
6. Complete GitHub login and consent.
7. After GitHub redirects back to the backend, copy the returned `access_token`.
8. Open Swagger and click `Authorize`.
9. Paste that token into the bearer auth dialog.

## Public API Endpoints

### `GET /api/v1/auth/github/login`

Generates a GitHub OAuth authorization URL and a short-lived state token.

### `GET /api/v1/github/repositories`

Fetch repositories for a GitHub user or organization.

Query parameters:

- `owner`: GitHub username or organization name
- `owner_type`: `user` or `org`
- `page`: page number
- `per_page`: page size

### `GET /api/v1/github/repositories/{owner}/{repo}/issues`

Lists issues for a repository. Pull requests are filtered out from this response.

Query parameters:

- `state`: `open`, `closed`, or `all`
- `page`: page number
- `per_page`: page size

### `POST /api/v1/github/repositories/{owner}/{repo}/pull-requests`

Creates a pull request in the target repository.

Request body:

```json
{
  "title": "Add API validation",
  "head": "feature/api-validation",
  "base": "main",
  "body": "This PR adds request validation for the connector.",
  "draft": false,
  "maintainer_can_modify": true
}
```

## Recommended Demo Sequence

1. Start the server.
2. Open `http://localhost:8000/docs`.
3. If you want to demonstrate OAuth, call `GET /api/v1/auth/github/login` and complete the browser flow.
4. Click `Authorize` in Swagger and paste your GitHub token or OAuth access token.
5. Call the repositories endpoint.
6. Call the issues endpoint.
7. Call the pull request endpoint.

## Optional Tests

Install development dependencies and run:

```powershell
py -3 -m pip install -r requirements-dev.txt
py -3 -m pytest -q
```

## Design Notes

- `app/clients/github.py` is the only module that talks directly to GitHub.
- `app/services/` contains connector logic and response mapping.
- `app/api/routes/` contains FastAPI route handlers only.
- Tokens and OAuth secrets are never hardcoded.
- OAuth state is short-lived and single-use.
