from uuid import UUID

from src.auth.application.dtos import UserDTO
from src.auth.domain.repositories import UserRepository


class GetMe:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, user_id: UUID) -> UserDTO | None:
        """Returns None if the user no longer exists or is inactive."""
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return UserDTO.from_entity(user)
