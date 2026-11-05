from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.api.schemas import RegisterRequest, UserResponse
from src.auth.application.register_user import RegisterUser
from src.auth.infrastructure.repositories import SqlAlchemyUserRepository
from src.shared.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


def get_register_user(db: Annotated[Session, Depends(get_db)]) -> RegisterUser:
    return RegisterUser(SqlAlchemyUserRepository(db))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user)],
) -> UserResponse:
    user = use_case.execute(request.email, request.username, request.password)
    if user is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email or username already taken")
    return UserResponse.model_validate(user)
