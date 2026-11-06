from uuid import UUID

from src.cashdoro.application.dtos import CashdoroDTO
from src.cashdoro.domain.repositories import CashdoroRepository


class GetCashdoro:
    def __init__(self, cashdoros: CashdoroRepository) -> None:
        self._cashdoros = cashdoros

    def execute(self, user_id: UUID) -> CashdoroDTO | None:
        """Returns None if the user has no cashdoro."""
        cashdoro = self._cashdoros.get_by_user_id(user_id)
        if cashdoro is None:
            return None
        return CashdoroDTO.from_entity(cashdoro)
