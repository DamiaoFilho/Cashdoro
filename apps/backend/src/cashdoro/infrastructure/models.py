from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import BaseEntity


class CashdoroModel(BaseEntity):
    __tablename__ = "cashdoros"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    session_time: Mapped[int] = mapped_column(server_default="25")
    pause_time: Mapped[int] = mapped_column(server_default="5")
    long_pause_time: Mapped[int] = mapped_column(server_default="15")
    sessions_until_long_break: Mapped[int] = mapped_column(server_default="4")
    hourly_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    total_earnings: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0")
