from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth.domain.refresh_token import RefreshToken
from src.auth.domain.user import User
from src.auth.infrastructure.models import RefreshTokenModel, UserModel


def to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        username=model.username,
        password_hash=model.password_hash,
        is_active=model.is_active,
        is_verified=model.is_verified,
    )


def to_model(user: User) -> UserModel:
    return UserModel(
        email=user.email,
        username=user.username,
        password_hash=user.password_hash,
        is_active=user.is_active,
        is_verified=user.is_verified,
    )


def refresh_token_to_model(token: RefreshToken) -> RefreshTokenModel:
    return RefreshTokenModel(
        user_id=token.user_id,
        token_hash=token.token_hash,
        expires_at=token.expires_at,
        revoked_at=token.revoked_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, user: User) -> User | None:
        model = to_model(user)
        self._session.add(model)
        try:
            self._session.flush()
        except IntegrityError:
            self._session.rollback()
            return None
        return to_entity(model)

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalar(select(UserModel).where(UserModel.email == email))
        return to_entity(model) if model else None

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self._session.get(UserModel, user_id)
        return to_entity(model) if model else None

    def commit(self) -> None:
        self._session.commit()


class SqlAlchemyRefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: RefreshToken) -> None:
        self._session.add(refresh_token_to_model(token))

    def commit(self) -> None:
        self._session.commit()
