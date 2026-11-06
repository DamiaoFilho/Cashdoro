from typing import Protocol
from uuid import UUID

from src.cashdoro.domain.cashdoro import Cashdoro


class CashdoroRepository(Protocol):
    def add(self, cashdoro: Cashdoro) -> None: ...

    def get_by_user_id(self, user_id: UUID) -> Cashdoro | None: ...
