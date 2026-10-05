from domain.account import Account

class AccountService:
    def __init__(self, repository):
        self._repository = repository

    def create_account(self, username: str, password: str) -> str:
        account = Account.create(username, password)  # domain validation
        self._repository.add(account)                 # persistence
        return account.username