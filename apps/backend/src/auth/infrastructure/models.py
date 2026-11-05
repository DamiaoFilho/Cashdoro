from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, false, true
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import BaseEntity


class UserModel(BaseEntity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default=true())
    is_verified: Mapped[bool] = mapped_column(server_default=false())


class RefreshTokenModel(BaseEntity):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
