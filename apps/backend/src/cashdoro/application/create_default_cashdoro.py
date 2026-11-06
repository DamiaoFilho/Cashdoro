from uuid import UUID

from src.cashdoro.domain.cashdoro import Cashdoro
from src.cashdoro.domain.repositories import CashdoroRepository


class CreateDefaultCashdoro:
    def __init__(self, cashdoros: CashdoroRepository) -> None:
        self._cashdoros = cashdoros

    def execute(self, user_id: UUID) -> None:
        """Does not commit: the caller owns the transaction (see RegisterUser)."""
        self._cashdoros.add(Cashdoro(user_id=user_id))
