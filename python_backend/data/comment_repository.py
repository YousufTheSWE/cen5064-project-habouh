from data.database import Database
from domain.comment import Comment


class SqliteCommentRepository:
    def __init__(self, database: Database):
        self._db = database
        self._init_tables()

    def _init_tables(self) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS comments ("
                "id INTEGER PRIMARY KEY, "
                "author_id INTEGER NOT NULL, "
                "post_id INTEGER NOT NULL, "
                "description TEXT NOT NULL, "
                "upvotes INTEGER DEFAULT 0, "
                "downvotes INTEGER DEFAULT 0)"
            )
            cursor = conn.execute("PRAGMA table_info(comments)")
            cols = [row[1] for row in cursor.fetchall()]
            if "upvotes" not in cols:
                conn.execute("ALTER TABLE comments ADD COLUMN upvotes INTEGER DEFAULT 0")
            if "downvotes" not in cols:
                conn.execute("ALTER TABLE comments ADD COLUMN downvotes INTEGER DEFAULT 0")
            if "is_approved" not in cols:
                conn.execute("ALTER TABLE comments ADD COLUMN is_approved INTEGER DEFAULT 0")

            conn.execute(
                "CREATE TABLE IF NOT EXISTS comment_votes ("
                "account_id INTEGER NOT NULL, "
                "comment_id INTEGER NOT NULL, "
                "vote_type INTEGER NOT NULL, "
                "PRIMARY KEY (account_id, comment_id))"
            )

    def add(self, comment: Comment) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO comments (id, author_id, post_id, description, upvotes, downvotes, is_approved) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    comment.id,
                    comment.author_id,
                    comment.post_id,
                    comment.description,
                    comment.upvotes,
                    comment.downvotes,
                    comment.is_approved,
                ),
            )

    def find_by_id(self, comment_id: int) -> Comment | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, author_id, post_id, description, "
                "COALESCE(upvotes, 0), COALESCE(downvotes, 0), COALESCE(is_approved, 0) "
                "FROM comments WHERE id = ?",
                (comment_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Comment(
                id=row[0],
                author_id=row[1],
                post_id=row[2],
                description=row[3],
                upvotes=row[4],
                downvotes=row[5],
                is_approved=row[6],
            )

    def list_by_post(self, post_id: int) -> list[Comment]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, author_id, post_id, description, "
                "COALESCE(upvotes, 0), COALESCE(downvotes, 0), COALESCE(is_approved, 0) "
                "FROM comments WHERE post_id = ? ORDER BY id ASC",
                (post_id,),
            )
            return [
                Comment(
                    id=row[0],
                    author_id=row[1],
                    post_id=row[2],
                    description=row[3],
                    upvotes=row[4],
                    downvotes=row[5],
                    is_approved=row[6],
                )
                for row in cursor.fetchall()
            ]

    def update(self, comment: Comment) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE comments SET description = ?, is_approved = 0 WHERE id = ?",
                (comment.description, comment.id),
            )

    def set_approved(self, comment_id: int, is_approved: int = 1) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE comments SET is_approved = ? WHERE id = ?",
                (is_approved, comment_id),
            )

    def delete(self, comment_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM comment_votes WHERE comment_id = ?", (comment_id,))
            conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))

    def get_user_vote(self, account_id: int, comment_id: int) -> int:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT vote_type FROM comment_votes WHERE account_id = ? AND comment_id = ?",
                (account_id, comment_id),
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def vote(self, account_id: int, comment_id: int, direction: int) -> tuple[int, int, int]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT vote_type FROM comment_votes WHERE account_id = ? AND comment_id = ?",
                (account_id, comment_id),
            )
            row = cursor.fetchone()
            current_vote = row[0] if row else 0

            if direction == 0 or current_vote == direction:
                new_vote = 0
            else:
                new_vote = 1 if direction > 0 else -1

            up_delta = 0
            down_delta = 0

            if current_vote == 1:
                up_delta -= 1
            elif current_vote == -1:
                down_delta -= 1

            if new_vote == 1:
                up_delta += 1
            elif new_vote == -1:
                down_delta += 1

            if new_vote == 0:
                conn.execute(
                    "DELETE FROM comment_votes WHERE account_id = ? AND comment_id = ?",
                    (account_id, comment_id),
                )
            else:
                conn.execute(
                    "INSERT INTO comment_votes (account_id, comment_id, vote_type) VALUES (?, ?, ?) "
                    "ON CONFLICT(account_id, comment_id) DO UPDATE SET vote_type = excluded.vote_type",
                    (account_id, comment_id, new_vote),
                )

            conn.execute(
                "UPDATE comments SET "
                "upvotes = MAX(0, COALESCE(upvotes, 0) + ?), "
                "downvotes = MAX(0, COALESCE(downvotes, 0) + ?) "
                "WHERE id = ?",
                (up_delta, down_delta, comment_id),
            )

            res = conn.execute(
                "SELECT COALESCE(upvotes, 0), COALESCE(downvotes, 0) FROM comments WHERE id = ?",
                (comment_id,),
            ).fetchone()
            return (res[0], res[1], new_vote)
