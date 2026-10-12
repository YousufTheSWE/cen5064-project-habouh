from domain.account import Account
from domain.errors import InvalidCredentialsError


class AccountService:
    def __init__(self, repository):
        self._repository = repository

    def create_account(self, username: str, password: str) -> str:
        account = Account.create(username, password)  # domain validation
        self._repository.add(account)                 # persistence
        return account.username

    def login(self, username: str, password: str) -> str:
        account = self._repository.find_by_username(username)
        if account is None or not account.verify_password(password):
            raise InvalidCredentialsError()
        return account.username