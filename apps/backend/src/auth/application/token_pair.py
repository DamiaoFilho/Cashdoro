from datetime import UTC, datetime, timedelta
from uuid import UUID

from src.auth.application.dtos import TokenPairDTO
from src.auth.domain.refresh_token import RefreshToken
from src.auth.domain.repositories import RefreshTokenRepository
from src.shared.config import Settings
from src.shared.security import create_access_token, generate_refresh_token, hash_refresh_token


def issue_token_pair(
    user_id: UUID, refresh_tokens: RefreshTokenRepository, settings: Settings
) -> TokenPairDTO:
    """Adds the new refresh token to the current transaction; the caller commits it."""
    access_token = create_access_token(
        str(user_id),
        settings.jwt_secret,
        timedelta(minutes=settings.access_token_expire_minutes),
    )
    refresh_token = generate_refresh_token()
    refresh_tokens.add(
        RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )
    )
    return TokenPairDTO(access_token=access_token, refresh_token=refresh_token)
