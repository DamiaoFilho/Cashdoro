from src.auth.application.dtos import TokenPairDTO
from src.auth.application.token_pair import issue_token_pair
from src.auth.domain.repositories import RefreshTokenRepository, UserRepository
from src.shared.config import Settings
from src.shared.security import verify_password


class LoginUser:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        settings: Settings,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._settings = settings

    def execute(self, email: str, password: str) -> TokenPairDTO | None:
        """Returns None if the credentials are wrong or the user is inactive."""
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None

        tokens = issue_token_pair(user.id, self._refresh_tokens, self._settings)
        self._refresh_tokens.commit()
        return tokens
