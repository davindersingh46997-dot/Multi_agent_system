from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def hash_password(password : str) -> str:
    """
    Produces a hash of the given password for verfication purposes .
    """

    return ph.hash(password)

def verify_password(password: str, hash_password : str) -> bool:
    """
    verify a plain text password against
    the stored hash password
    """

    try:
        return ph.verify(
            hash_password,
            password
        )

    except VerifyMismatchError:
        return False