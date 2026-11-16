import sqlite3
import time

from data.database import Database
from domain.account import Account
from domain.errors import UsernameAlreadyExistsError
from domain.snowflake import generate_snowflake


class SqliteAccountRepository:
    def __init__(self, database: Database):
        self._db = database
        self._init_tables()

    def _init_tables(self) -> None:
        with self._db.connect() as conn:
            cursor = conn.execute("PRAGMA table_info(accounts)")
            columns = [row[1] for row in cursor.fetchall()]
            if not columns:
                conn.execute(
                    "CREATE TABLE accounts ("
                    "id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)"
                )
            elif "id" not in columns:
                conn.execute("ALTER TABLE accounts RENAME TO accounts_old")
                conn.execute(
                    "CREATE TABLE accounts ("
                    "id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)"
                )
                old_rows = conn.execute("SELECT username, password_hash FROM accounts_old").fetchall()
                for u, p in old_rows:
                    conn.execute(
                        "INSERT INTO accounts (id, username, password_hash) VALUES (?, ?, ?)",
                        (generate_snowflake(), u, p),
                    )
                conn.execute("DROP TABLE accounts_old")

            conn.execute(
                "CREATE TABLE IF NOT EXISTS auth_tokens ("
                "token TEXT PRIMARY KEY, account_id INTEGER NOT NULL, created_at INTEGER NOT NULL)"
            )

    def add(self, account: Account) -> None:
        try:
            with self._db.connect() as conn:
                conn.execute(
                    "INSERT INTO accounts (id, username, password_hash) VALUES (?, ?, ?)",
                    (account.id, account.username, account.password_hash),
                )
        except sqlite3.IntegrityError:
            raise UsernameAlreadyExistsError() from None

    def find_by_username(self, username: str) -> Account | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, username, password_hash FROM accounts WHERE username = ?",
                (username,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Account(id=row[0], username=row[1], password_hash=row[2])

    def find_by_id(self, account_id: int) -> Account | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, username, password_hash FROM accounts WHERE id = ?",
                (account_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Account(id=row[0], username=row[1], password_hash=row[2])

    def is_username_available(self, username: str, exclude_account_id: int | None = None) -> bool:
        with self._db.connect() as conn:
            if exclude_account_id is not None:
                cursor = conn.execute(
                    "SELECT 1 FROM accounts WHERE username = ? AND id != ?",
                    (username, exclude_account_id),
                )
            else:
                cursor = conn.execute(
                    "SELECT 1 FROM accounts WHERE username = ?",
                    (username,),
                )
            return cursor.fetchone() is None

    def update_username(self, account_id: int, new_username: str) -> None:
        try:
            with self._db.connect() as conn:
                conn.execute(
                    "UPDATE accounts SET username = ? WHERE id = ?",
                    (new_username, account_id),
                )
        except sqlite3.IntegrityError:
            raise UsernameAlreadyExistsError() from None

    def update_password(self, account_id: int, new_password_hash: str) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE accounts SET password_hash = ? WHERE id = ?",
                (new_password_hash, account_id),
            )

    def save_token(self, token: str, account_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO auth_tokens (token, account_id, created_at) VALUES (?, ?, ?)",
                (token, account_id, int(time.time())),
            )

    def find_account_id_by_token(self, token: str) -> int | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT account_id FROM auth_tokens WHERE token = ?",
                (token,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return row[0]

    def delete_token(self, token: str) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
