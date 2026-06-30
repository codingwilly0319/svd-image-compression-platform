from __future__ import annotations

from dataclasses import dataclass


class AuthenticationError(ValueError):
    """Raised when a user cannot be authenticated."""


@dataclass(frozen=True, slots=True)
class User:
    username: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class UserManager:
    def __init__(self, users: dict[str, dict[str, str]] | None = None) -> None:
        self.users = users or {
            "operator": {"password": "operator123", "role": "operator"},
            "admin": {"password": "admin123", "role": "admin"},
        }

    def authenticate(self, username: str, password: str) -> User:
        account = self.users.get(username.strip())
        if account is None or account["password"] != password:
            raise AuthenticationError("Invalid username or password.")
        return User(username=username.strip(), role=account["role"])
