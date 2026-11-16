import secrets

from domain.account import Account
from domain.errors import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)


class AccountService:
    def __init__(self, repository):
        self._repository = repository

    def create_account(self, username: str, password: str) -> dict:
        account = Account.create(username, password)  # domain validation + snowflake id
        self._repository.add(account)                 # persistence
        token = secrets.token_urlsafe(32)
        self._repository.save_token(token, account.id)
        return {
            "account_id": account.id,
            "username": account.username,
            "auth_token": token,
        }

    def login(self, username: str, password: str) -> dict:
        account = self._repository.find_by_username(username)
        if account is None or not account.verify_password(password):
            raise InvalidCredentialsError()
        token = secrets.token_urlsafe(32)
        self._repository.save_token(token, account.id)
        return {
            "account_id": account.id,
            "username": account.username,
            "auth_token": token,
        }

    def get_account_id_from_token(self, token: str) -> int:
        account_id = self._repository.find_account_id_by_token(token)
        if account_id is None:
            raise AuthenticationRequiredError()
        return account_id

    def get_account_by_token(self, token: str) -> Account:
        account_id = self.get_account_id_from_token(token)
        account = self._repository.find_by_id(account_id)
        if account is None:
            raise AuthenticationRequiredError()
        return account

    def get_username_by_id(self, account_id: int) -> str:
        account = self._repository.find_by_id(account_id)
        return account.username if account else f"user_{account_id}"

    def is_username_available(self, username: str, exclude_account_id: int | None = None) -> bool:
        clean = username.strip()
        if not clean:
            return False
        return self._repository.is_username_available(clean, exclude_account_id)

    def update_username(self, account_id: int, new_username: str) -> str:
        Account.validate_username(new_username)
        if not self.is_username_available(new_username, exclude_account_id=account_id):
            raise UsernameAlreadyExistsError()
        self._repository.update_username(account_id, new_username)
        return new_username

    def update_password(self, account_id: int, current_password: str, new_password: str) -> None:
        account = self._repository.find_by_id(account_id)
        if account is None or not account.verify_password(current_password):
            raise InvalidCredentialsError("Current password is incorrect")
        new_hash = Account.hash_password(new_password)
        self._repository.update_password(account_id, new_hash)

    def find_account_by_identifier(self, identifier: str) -> Account | None:
        clean = str(identifier).strip()
        if clean.isdigit():
            account = self._repository.find_by_id(int(clean))
            if account:
                return account
        return self._repository.find_by_username(clean)

    def logout(self, token: str) -> None:
        self._repository.delete_token(token)
