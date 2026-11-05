import bcrypt

BCRYPT_COST_FACTOR = 12


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=BCRYPT_COST_FACTOR)
    return bcrypt.hashpw(password.encode(), salt).decode()
