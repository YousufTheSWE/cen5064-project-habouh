import hashlib
import hmac
import secrets
from dataclasses import dataclass

from domain.errors import InvalidUsernameError, PasswordTooShortError
from domain.snowflake import generate_snowflake

MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class Account:
    id: int
    username: str
    password_hash: str  # "salt_hex:hash_hex"

    @staticmethod
    def validate_username(username: str) -> None:
        if not (username.isascii() and username.isalnum()):  # also rejects empty string
            raise InvalidUsernameError()

    @staticmethod
    def validate_password(password: str) -> None:
        if len(password) < MIN_PASSWORD_LENGTH:
            raise PasswordTooShortError()

    @staticmethod
    def hash_password(password: str) -> str:
        Account.validate_password(password)
        salt = secrets.token_bytes(16)
        digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return f"{salt.hex()}:{digest.hex()}"

    @staticmethod
    def create(username: str, password: str, account_id: int | None = None) -> "Account":
        Account.validate_username(username)
        resolved_id = account_id if account_id is not None else generate_snowflake()
        return Account(resolved_id, username, Account.hash_password(password))

    def verify_password(self, password: str) -> bool:
        return _verify_password(password, self.password_hash)


def _verify_password(password: str, password_hash: str) -> bool:
    try:
        salt_hex, digest_hex = password_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_digest = bytes.fromhex(digest_hex)
        actual_digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
        return hmac.compare_digest(actual_digest, expected_digest)
    except ValueError:
        return False
