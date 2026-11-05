from sqlalchemy import false, true
from sqlalchemy.orm import Mapped, mapped_column

from src.shared.database import BaseEntity


class UserModel(BaseEntity):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(server_default=true())
    is_verified: Mapped[bool] = mapped_column(server_default=false())
