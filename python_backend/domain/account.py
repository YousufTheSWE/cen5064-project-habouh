import hashlib
import random
from dataclasses import dataclass

from domain.errors import InvalidUsernameError, PasswordTooShortError

MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class Account:
    username: str
    password_hash: str  # "salt_hex:hash_hex"

    @staticmethod
    def create(username: str, password: str) -> "Account":
        if not (username.isascii() and username.isalnum()):  # also rejects empty string
            raise InvalidUsernameError()
        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordTooShortError()
        return Account(username, _hash_password(password))


def _hash_password(password: str) -> str:
    salt = random.randbytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"