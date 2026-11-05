from typing import Protocol

from src.auth.domain.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> User | None:
        """Store a new user. Returns None if the email or username is already taken."""
        ...

    def commit(self) -> None: ...
