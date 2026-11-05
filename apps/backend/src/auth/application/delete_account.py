from uuid import UUID

from src.auth.domain.repositories import UserRepository


class DeleteAccount:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> None:
        self._users.delete(user_id)
        self._users.commit()
