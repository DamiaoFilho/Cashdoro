from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class Cashdoro:
    user_id: UUID
    session_time: int = 25
    pause_time: int = 5
    long_pause_time: int = 15
    sessions_until_long_break: int = 4
    hourly_rate: Decimal | None = None
    total_earnings: Decimal = Decimal("0")
    id: UUID | None = None
