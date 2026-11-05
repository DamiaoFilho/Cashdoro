from datetime import UTC, datetime, timedelta

from src.auth.application.dtos import TokenPairDTO
from src.auth.domain.refresh_token import RefreshToken
from src.auth.domain.repositories import RefreshTokenRepository, UserRepository
from src.shared.config import Settings
from src.shared.security import (
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    verify_password,
)


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

        access_token = create_access_token(
            str(user.id),
            self._settings.jwt_secret,
            timedelta(minutes=self._settings.access_token_expire_minutes),
        )
        refresh_token = generate_refresh_token()
        self._refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                token_hash=hash_refresh_token(refresh_token),
                expires_at=datetime.now(UTC)
                + timedelta(days=self._settings.refresh_token_expire_days),
            )
        )
        self._refresh_tokens.commit()
        return TokenPairDTO(access_token=access_token, refresh_token=refresh_token)
