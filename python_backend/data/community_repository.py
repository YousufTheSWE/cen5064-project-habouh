from data.database import Database
from domain.community import Community


class SqliteCommunityRepository:
    def __init__(self, database: Database):
        self._db = database
        self._db.ensure_table(
            "CREATE TABLE IF NOT EXISTS communities ("
            "id INTEGER PRIMARY KEY, "
            "owner_id INTEGER NOT NULL, "
            "name TEXT NOT NULL, "
            "description TEXT NOT NULL, "
            "picture TEXT NOT NULL)"
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
            conn.execute("DELETE FROM communities WHERE id = ?", (community_id,))
