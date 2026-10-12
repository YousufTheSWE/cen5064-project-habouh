import hashlib
import hmac
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

    def verify_password(self, password: str) -> bool:
        return _verify_password(password, self.password_hash)


def _hash_password(password: str) -> str:
    salt = random.randbytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return f"{salt.hex()}:{digest.hex()}"


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
        actual_digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual_digest, expected_digest)
    except ValueError:
        return False
