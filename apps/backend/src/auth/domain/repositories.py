from typing import Protocol
from uuid import UUID

from src.auth.domain.refresh_token import RefreshToken
from src.auth.domain.user import User


class UserRepository(Protocol):
    def add(self, user: User) -> User | None:
        """Store a new user. Returns None if the email or username is already taken."""
        ...

    def get_by_email(self, email: str) -> User | None: ...

    def get_by_id(self, user_id: UUID) -> User | None: ...

    def delete(self, user_id: UUID) -> None:
        """Hard delete. Data owned by the user is removed by ON DELETE CASCADE."""
        ...

    def commit(self) -> None: ...


class RefreshTokenRepository(Protocol):
    def add(self, token: RefreshToken) -> None: ...

    def get_by_hash_for_update(self, token_hash: str) -> RefreshToken | None:
        """Locks the row until the transaction ends, so a token can only be rotated once."""
        ...

    def save_revocation(self, token: RefreshToken) -> None: ...

    def commit(self) -> None: ...
