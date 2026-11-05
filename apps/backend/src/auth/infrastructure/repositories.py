from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth.domain.user import User
from src.auth.infrastructure.models import UserModel


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

    def commit(self) -> None:
        self._session.commit()
