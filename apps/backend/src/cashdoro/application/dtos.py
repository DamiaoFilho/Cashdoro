from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from src.cashdoro.domain.cashdoro import Cashdoro


@dataclass(frozen=True)
class CashdoroDTO:
    id: UUID
    user_id: UUID
    session_time: int
    pause_time: int
    long_pause_time: int
    sessions_until_long_break: int
    hourly_rate: Decimal | None
    total_earnings: Decimal

    @classmethod
    def from_entity(cls, cashdoro: Cashdoro) -> CashdoroDTO:
        return cls(
            id=cashdoro.id,
            user_id=cashdoro.user_id,
            session_time=cashdoro.session_time,
            pause_time=cashdoro.pause_time,
            long_pause_time=cashdoro.long_pause_time,
            sessions_until_long_break=cashdoro.sessions_until_long_break,
            hourly_rate=cashdoro.hourly_rate,
            total_earnings=cashdoro.total_earnings,
        )
