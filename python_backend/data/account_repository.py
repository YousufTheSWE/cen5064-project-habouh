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

    def find_by_username(self, username: str) -> Account | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT username, password_hash FROM accounts WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Account(username=row[0], password_hash=row[1])