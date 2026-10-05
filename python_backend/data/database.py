import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path


class Database:
    def __init__(self, path: str):
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)  # create missing folders

    @contextmanager
    def connect(self):
        # sqlite3 creates the .db file itself if it doesn't exist.
        # Transaction (commit/rollback) plus guaranteed close.
        with closing(sqlite3.connect(self._path)) as conn, conn:
            yield conn

    def ensure_table(self, create_sql: str) -> None:
        with self.connect() as conn:
            conn.execute(create_sql)