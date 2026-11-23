import time

from data.database import Database
from domain.community import Community


class SqliteCommunityRepository:
    def __init__(self, database: Database):
        self._db = database
        self._init_tables()

    def _init_tables(self) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS communities ("
                "id INTEGER PRIMARY KEY, "
                "owner_id INTEGER NOT NULL, "
                "name TEXT NOT NULL, "
                "description TEXT NOT NULL, "
                "picture TEXT NOT NULL)"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS community_moderators ("
                "community_id INTEGER NOT NULL, "
                "account_id INTEGER NOT NULL, "
                "PRIMARY KEY (community_id, account_id))"
            )
            conn.execute(
                "CREATE TABLE IF NOT EXISTS community_banned_users ("
                "community_id INTEGER NOT NULL, "
                "account_id INTEGER NOT NULL, "
                "banned_by_id INTEGER NOT NULL, "
                "created_at INTEGER NOT NULL, "
                "PRIMARY KEY (community_id, account_id))"
            )

    def add(self, community: Community) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO communities (id, owner_id, name, description, picture) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    community.id,
                    community.owner_id,
                    community.name,
                    community.description,
                    community.picture,
                ),
            )

    def find_by_id(self, community_id: int) -> Community | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, owner_id, name, description, picture FROM communities WHERE id = ?",
                (community_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Community(
                id=row[0],
                owner_id=row[1],
                name=row[2],
                description=row[3],
                picture=row[4],
            )

    def list_all(self) -> list[Community]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, owner_id, name, description, picture FROM communities ORDER BY id DESC"
            )
            return [
                Community(
                    id=row[0],
                    owner_id=row[1],
                    name=row[2],
                    description=row[3],
                    picture=row[4],
                )
                for row in cursor.fetchall()
            ]

    def count_by_owner(self, owner_id: int) -> int:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM communities WHERE owner_id = ?",
                (owner_id,),
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def update(self, community: Community) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE communities SET name = ?, description = ?, picture = ? WHERE id = ?",
                (community.name, community.description, community.picture, community.id),
            )

    def transfer_ownership(self, community_id: int, new_owner_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE communities SET owner_id = ? WHERE id = ?",
                (new_owner_id, community_id),
            )

    def delete(self, community_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM community_moderators WHERE community_id = ?", (community_id,))
            conn.execute("DELETE FROM community_banned_users WHERE community_id = ?", (community_id,))
            conn.execute("DELETE FROM communities WHERE id = ?", (community_id,))

    # Moderator Management
    def add_moderator(self, community_id: int, account_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO community_moderators (community_id, account_id) VALUES (?, ?)",
                (community_id, account_id),
            )

    def remove_moderator(self, community_id: int, account_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM community_moderators WHERE community_id = ? AND account_id = ?",
                (community_id, account_id),
            )

    def list_moderators(self, community_id: int) -> list[int]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT account_id FROM community_moderators WHERE community_id = ? ORDER BY account_id ASC",
                (community_id,),
            )
            return [row[0] for row in cursor.fetchall()]

    def is_moderator(self, community_id: int, account_id: int) -> bool:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM community_moderators WHERE community_id = ? AND account_id = ?",
                (community_id, account_id),
            )
            return cursor.fetchone() is not None

    # Banned User Management
    def ban_user(self, community_id: int, account_id: int, banned_by_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO community_banned_users (community_id, account_id, banned_by_id, created_at) "
                "VALUES (?, ?, ?, ?)",
                (community_id, account_id, banned_by_id, int(time.time())),
            )

    def unban_user(self, community_id: int, account_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM community_banned_users WHERE community_id = ? AND account_id = ?",
                (community_id, account_id),
            )

    def list_banned(self, community_id: int) -> list[dict]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT account_id, banned_by_id, created_at "
                "FROM community_banned_users WHERE community_id = ? ORDER BY created_at DESC",
                (community_id,),
            )
            return [
                {
                    "account_id": row[0],
                    "banned_by_id": row[1],
                    "created_at": row[2],
                }
                for row in cursor.fetchall()
            ]

    def is_banned(self, community_id: int, account_id: int) -> bool:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM community_banned_users WHERE community_id = ? AND account_id = ?",
                (community_id, account_id),
            )
            return cursor.fetchone() is not None
