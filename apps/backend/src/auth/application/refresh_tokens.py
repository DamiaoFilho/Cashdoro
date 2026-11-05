from datetime import UTC, datetime

from src.auth.application.dtos import TokenPairDTO
from src.auth.application.token_pair import issue_token_pair
from src.auth.domain.repositories import RefreshTokenRepository, UserRepository
from src.shared.config import Settings
from src.shared.security import hash_refresh_token


class RefreshTokens:
    def __init__(
        self,
        users: UserRepository,
        refresh_tokens: RefreshTokenRepository,
        settings: Settings,
    ) -> None:
        self._users = users
        self._refresh_tokens = refresh_tokens
        self._settings = settings

    def execute(self, refresh_token: str) -> TokenPairDTO | None:
        """Returns None if the token is not valid or the user is inactive."""
        now = datetime.now(UTC)
        token = self._refresh_tokens.get_by_hash_for_update(hash_refresh_token(refresh_token))
        if token is None or not token.is_valid(now):
            return None

        user = self._users.get_by_id(token.user_id)
        if user is None or not user.is_active:
            return None

        token.revoke(now)
        self._refresh_tokens.save_revocation(token)
        tokens = issue_token_pair(user.id, self._refresh_tokens, self._settings)
        self._refresh_tokens.commit()
        return tokens
