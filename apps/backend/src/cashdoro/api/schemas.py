from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CashdoroResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    session_time: int
    pause_time: int
    long_pause_time: int
    sessions_until_long_break: int
    hourly_rate: Decimal | None
    total_earnings: Decimal
