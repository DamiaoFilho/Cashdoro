from decimal import Decimal
from uuid import UUID

from src.cashdoro.application.dtos import CashdoroDTO
from src.cashdoro.domain.repositories import CashdoroRepository


class UpdateCashdoro:
    def __init__(self, cashdoros: CashdoroRepository) -> None:
        self._cashdoros = cashdoros

    def execute(
        self,
        user_id: UUID,
        session_time: int,
        pause_time: int,
        long_pause_time: int,
        sessions_until_long_break: int,
        hourly_rate: Decimal | None,
    ) -> CashdoroDTO | None:
        """Returns None if the user has no cashdoro."""
        cashdoro = self._cashdoros.get_by_user_id(user_id)
        if cashdoro is None:
            return None

        cashdoro.change_settings(
            session_time, pause_time, long_pause_time, sessions_until_long_break, hourly_rate
        )
        self._cashdoros.save_settings(cashdoro)
        self._cashdoros.commit()
        return CashdoroDTO.from_entity(cashdoro)
