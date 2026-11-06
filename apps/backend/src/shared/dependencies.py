from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src.auth.application.dtos import UserDTO
from src.auth.application.get_me import GetMe
from src.auth.infrastructure.repositories import SqlAlchemyUserRepository
from src.cashdoro.application.create_default_cashdoro import CreateDefaultCashdoro
from src.cashdoro.infrastructure.repositories import SqlAlchemyCashdoroRepository
from src.shared.config import Settings, get_settings
from src.shared.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


def get_create_default_cashdoro(db: Annotated[Session, Depends(get_db)]) -> CreateDefaultCashdoro:
    return CreateDefaultCashdoro(SqlAlchemyCashdoroRepository(db))


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserDTO:
    unauthorized = HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        "Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    subject = decode_access_token(token, settings.jwt_secret)
    if subject is None:
        raise unauthorized
    try:
        user_id = UUID(subject)
    except ValueError:
        raise unauthorized from None

    user = GetMe(SqlAlchemyUserRepository(db)).execute(user_id)
    if user is None:
        raise unauthorized
    return user
