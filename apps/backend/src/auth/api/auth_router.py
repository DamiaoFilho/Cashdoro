from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.auth.api.schemas import (
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    normalize_email,
)
from src.auth.application.login_user import LoginUser
from src.auth.application.logout_user import LogoutUser
from src.auth.application.refresh_tokens import RefreshTokens
from src.auth.application.register_user import RegisterUser
from src.auth.infrastructure.repositories import (
    SqlAlchemyRefreshTokenRepository,
    SqlAlchemyUserRepository,
)
from src.shared.config import Settings, get_settings
from src.shared.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def get_register_user(db: Annotated[Session, Depends(get_db)]) -> RegisterUser:
    return RegisterUser(SqlAlchemyUserRepository(db))


def get_login_user(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> LoginUser:
    return LoginUser(SqlAlchemyUserRepository(db), SqlAlchemyRefreshTokenRepository(db), settings)


def get_refresh_tokens(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RefreshTokens:
    return RefreshTokens(
        SqlAlchemyUserRepository(db), SqlAlchemyRefreshTokenRepository(db), settings
    )


def get_logout_user(db: Annotated[Session, Depends(get_db)]) -> LogoutUser:
    return LogoutUser(SqlAlchemyRefreshTokenRepository(db))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
) -> UserResponse:
    user = use_case.execute(request.email, request.username, request.password)
    if user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email or username already taken")
    return UserResponse.model_validate(user)


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: Annotated[LoginUser, Depends(get_login_user)],
) -> TokenResponse:
    # OAuth2 Password Flow requires the field to be named "username"; it carries the email.
    tokens = use_case.execute(normalize_email(form.username), form.password)
    if tokens is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse.model_validate(tokens)


@router.post("/refresh")
def refresh(
    request: RefreshRequest,
    use_case: Annotated[RefreshTokens, Depends(get_refresh_tokens)],
) -> TokenResponse:
    tokens = use_case.execute(request.refresh_token)
    if tokens is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse.model_validate(tokens)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: RefreshRequest,
    use_case: Annotated[LogoutUser, Depends(get_logout_user)],
) -> None:
    use_case.execute(request.refresh_token)
