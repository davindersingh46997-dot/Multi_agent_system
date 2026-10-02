from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from brain.core.settings import get_settings

ph = PasswordHasher()
ALGORITHM = "HS256"

def hash_password(password : str) -> str:
    """
    Produces a hash of the given password for verfication purposes .
    """

    return ph.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """
    verify a plain text password against
    the stored hash password
    """

    try:
        return ph.verify(
            password_hash,
            password
        )

    except (InvalidHashError, VerifyMismatchError):
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expires_at},
        settings.signing_secret(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(
            token,
            get_settings().signing_secret(),
            algorithms=[ALGORITHM],
        )
        subject = payload.get("sub")
        return int(subject) if subject is not None else None
    except (jwt.InvalidTokenError, RuntimeError, TypeError, ValueError):
        return None