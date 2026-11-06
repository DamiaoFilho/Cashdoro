from src.auth.application.dtos import UserDTO
from src.auth.domain.repositories import UserRepository
from src.auth.domain.user import User
from src.cashdoro.application.create_default_cashdoro import CreateDefaultCashdoro
from src.shared.security import hash_password


class RegisterUser:
    def __init__(
        self, users: UserRepository, create_default_cashdoro: CreateDefaultCashdoro
    ) -> None:
        self._users = users
        self._create_default_cashdoro = create_default_cashdoro

    def execute(self, email: str, username: str, password: str) -> UserDTO | None:
        """Returns None if the email or username is already taken."""
        user = self._users.add(
            User(email=email, username=username, password_hash=hash_password(password))
        )
        if user is None:
            return None

        self._create_default_cashdoro.execute(user.id)
        self._users.commit()
        return UserDTO.from_entity(user)
