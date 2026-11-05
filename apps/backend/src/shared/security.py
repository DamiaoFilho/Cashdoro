import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

BCRYPT_COST_FACTOR = 12
BCRYPT_MAX_PASSWORD_BYTES = 72
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_COST_FACTOR)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    encoded = password.encode()
    # bcrypt rejects longer inputs, and no stored password can be longer than this.
    if len(encoded) > BCRYPT_MAX_PASSWORD_BYTES:
        return False
    return bcrypt.checkpw(encoded, password_hash.encode())


def create_access_token(subject: str, secret: str, expires_in: timedelta) -> str:
    now = datetime.now(UTC)
    claims = {"sub": subject, "iat": now, "exp": now + expires_in}
    return jwt.encode(claims, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, secret: str) -> str | None:
    """Returns the token subject, or None if the token is invalid or expired."""
    try:
        claims = jwt.decode(
            token, secret, algorithms=[JWT_ALGORITHM], options={"require": ["exp", "sub"]}
        )
    except jwt.InvalidTokenError:
        return None
    return claims["sub"]


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
