from typing import Protocol
from uuid import UUID

from src.cashdoro.domain.cashdoro import Cashdoro


class CashdoroRepository(Protocol):
    def add(self, cashdoro: Cashdoro) -> None: ...

    def get_by_user_id(self, user_id: UUID) -> Cashdoro | None: ...

    def save_settings(self, cashdoro: Cashdoro) -> None:
        """Writes the editable settings only, never total_earnings."""
        ...

    def commit(self) -> None: ...
