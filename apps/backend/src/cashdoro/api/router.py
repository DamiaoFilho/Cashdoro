from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.application.dtos import UserDTO
from src.cashdoro.api.schemas import CashdoroResponse
from src.cashdoro.application.get_cashdoro import GetCashdoro
from src.cashdoro.infrastructure.repositories import SqlAlchemyCashdoroRepository
from src.shared.dependencies import get_current_user, get_db

router = APIRouter(prefix="/cashdoro", tags=["cashdoro"])


def get_get_cashdoro(db: Annotated[Session, Depends(get_db)]) -> GetCashdoro:
    return GetCashdoro(SqlAlchemyCashdoroRepository(db))


@router.get("")
def get_cashdoro(
    current_user: Annotated[UserDTO, Depends(get_current_user)],
    use_case: Annotated[GetCashdoro, Depends(get_get_cashdoro)],
) -> CashdoroResponse:
    cashdoro = use_case.execute(current_user.id)
    if cashdoro is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cashdoro not found")
    return CashdoroResponse.model_validate(cashdoro)
