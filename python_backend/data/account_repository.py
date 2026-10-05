import sqlite3

from data.database import Database
from domain.account import Account
from domain.errors import UsernameAlreadyExistsError


class SqliteAccountRepository:
    def __init__(self, database: Database):
        self._db = database
        self._db.ensure_table(
            "CREATE TABLE IF NOT EXISTS accounts ("
            "username TEXT PRIMARY KEY, password_hash TEXT NOT NULL)"
        )

    def add(self, account: Account) -> None:
        try:
            with self._db.connect() as conn:
                conn.execute(
                    "INSERT INTO accounts (username, password_hash) VALUES (?, ?)",
                    (account.username, account.password_hash),
                )
        except sqlite3.IntegrityError:
            raise UsernameAlreadyExistsError() from None