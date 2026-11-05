from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.api.schemas import UserResponse
from src.auth.application.dtos import UserDTO
from src.shared.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: Annotated[UserDTO, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)
