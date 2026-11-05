from src.auth.application.dtos import UserDTO
from src.auth.domain.repositories import UserRepository
from src.auth.domain.user import User
from src.shared.security import hash_password


class RegisterUser:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def execute(self, email: str, username: str, password: str) -> UserDTO | None:
        """Returns None if the email or username is already taken."""
        user = self._users.add(
            User(email=email, username=username, password_hash=hash_password(password))
        )
        if user is None:
            return None

        self._users.commit()
        return UserDTO.from_entity(user)
