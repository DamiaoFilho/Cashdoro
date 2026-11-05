from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RefreshToken:
    user_id: UUID
    token_hash: str
    expires_at: datetime
    revoked_at: datetime | None = None
    id: UUID | None = None

    def is_valid(self, now: datetime) -> bool:
        return self.revoked_at is None and now < self.expires_at

    def revoke(self, now: datetime) -> None:
        self.revoked_at = now
