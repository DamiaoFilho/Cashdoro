from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.api.schemas import UserResponse
from src.auth.application.delete_account import DeleteAccount
from src.auth.application.dtos import UserDTO
from src.auth.infrastructure.repositories import SqlAlchemyUserRepository
from src.shared.dependencies import get_current_user, get_db

router = APIRouter(prefix="/users", tags=["users"])


def get_delete_account(db: Annotated[Session, Depends(get_db)]) -> DeleteAccount:
    return DeleteAccount(SqlAlchemyUserRepository(db))


@router.get("/me")
def get_me(current_user: Annotated[UserDTO, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    use_case: Annotated[DeleteAccount, Depends(get_delete_account)],
) -> None:
    use_case.execute(current_user.id)
