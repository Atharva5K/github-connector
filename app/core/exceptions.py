from __future__ import annotations


class ConnectorError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(ConnectorError):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(message=message, status_code=400)


class GitHubAPIError(ConnectorError):
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message=message, status_code=status_code)
