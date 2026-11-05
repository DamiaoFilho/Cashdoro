from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    email: str
    username: str
    password_hash: str
    is_active: bool = True
    is_verified: bool = False
    id: UUID | None = None
