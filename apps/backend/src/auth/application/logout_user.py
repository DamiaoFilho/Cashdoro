from datetime import UTC, datetime

from src.auth.domain.repositories import RefreshTokenRepository
from src.shared.security import hash_refresh_token


class LogoutUser:
    def __init__(self, refresh_tokens: RefreshTokenRepository) -> None:
        self._refresh_tokens = refresh_tokens

    def execute(self, refresh_token: str) -> None:
        """Unknown or already invalid tokens are ignored: the session is over either way."""
        now = datetime.now(UTC)
        token = self._refresh_tokens.get_by_hash_for_update(hash_refresh_token(refresh_token))
        if token is None or not token.is_valid(now):
            return

        token.revoke(now)
        self._refresh_tokens.save_revocation(token)
        self._refresh_tokens.commit()
