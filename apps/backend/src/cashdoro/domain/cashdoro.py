from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
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

    def change_settings(
        self,
        session_time: int,
        pause_time: int,
        long_pause_time: int,
        sessions_until_long_break: int,
        hourly_rate: Decimal | None,
    ) -> None:
        self.session_time = session_time
        self.pause_time = pause_time
        self.long_pause_time = long_pause_time
        self.sessions_until_long_break = sessions_until_long_break
        self.hourly_rate = (
            None
            if hourly_rate is None
            else hourly_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)
        )
