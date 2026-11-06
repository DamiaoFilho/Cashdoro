from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UpdateCashdoroRequest(BaseModel):
    session_time: int = Field(ge=1, le=180)
    pause_time: int = Field(ge=1, le=60)
    long_pause_time: int = Field(ge=1, le=120)
    sessions_until_long_break: int = Field(ge=1, le=12)
    hourly_rate: Decimal | None = Field(ge=0, le=100000, decimal_places=2)


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
