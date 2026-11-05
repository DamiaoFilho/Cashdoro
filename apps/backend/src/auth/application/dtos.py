from dataclasses import dataclass
from uuid import UUID

from src.auth.domain.user import User


@dataclass(frozen=True)
class TokenPairDTO:
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class UserDTO:
    id: UUID
    email: str
    username: str
    is_active: bool
    is_verified: bool

    @classmethod
    def from_entity(cls, user: User) -> UserDTO:
        return cls(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )
