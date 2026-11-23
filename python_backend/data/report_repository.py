import time

from data.database import Database
from domain.snowflake import generate_snowflake


class SqliteReportRepository:
    def __init__(self, database: Database):
        self._db = database
        self._init_tables()

    def _init_tables(self) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS reports ("
                "id INTEGER PRIMARY KEY, "
                "community_id INTEGER NOT NULL, "
                "target_type TEXT NOT NULL, "  # 'post' or 'comment'
                "target_id INTEGER NOT NULL, "
                "reporter_id INTEGER NOT NULL, "
                "created_at INTEGER NOT NULL, "
                "UNIQUE(target_type, target_id, reporter_id))"
            )

    def add_report(
        self,
        community_id: int,
        target_type: str,
        target_id: int,
        reporter_id: int,
    ) -> int:
        report_id = generate_snowflake()
        with self._db.connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO reports (id, community_id, target_type, target_id, reporter_id, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (report_id, community_id, target_type, target_id, reporter_id, int(time.time())),
            )
        return report_id

    def has_user_reported(self, target_type: str, target_id: int, reporter_id: int) -> bool:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM reports WHERE target_type = ? AND target_id = ? AND reporter_id = ?",
                (target_type, target_id, reporter_id),
            )
            return cursor.fetchone() is not None

    def list_reports_by_community(self, community_id: int) -> list[dict]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT target_type, target_id, reporter_id, created_at "
                "FROM reports WHERE community_id = ? ORDER BY created_at DESC",
                (community_id,),
            )
            rows = cursor.fetchall()

        # Group by (target_type, target_id)
        grouped: dict[tuple[str, int], dict] = {}
        for target_type, target_id, reporter_id, created_at in rows:
            key = (target_type, target_id)
            if key not in grouped:
                grouped[key] = {
                    "target_type": target_type,
                    "target_id": target_id,
                    "community_id": community_id,
                    "reporter_ids": [],
                    "latest_report_time": created_at,
                }
            grouped[key]["reporter_ids"].append(reporter_id)

        return list(grouped.values())

    def delete_reports_for_target(self, target_type: str, target_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "DELETE FROM reports WHERE target_type = ? AND target_id = ?",
                (target_type, target_id),
            )

    def delete_reports_by_community(self, community_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM reports WHERE community_id = ?", (community_id,))
