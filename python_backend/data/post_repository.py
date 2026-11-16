from data.database import Database
from domain.post import Post


class SqlitePostRepository:
    def __init__(self, database: Database):
        self._db = database
        self._init_tables()

    def _init_tables(self) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS posts ("
                "id INTEGER PRIMARY KEY, "
                "author_id INTEGER NOT NULL, "
                "community_id INTEGER NOT NULL, "
                "name TEXT NOT NULL, "
                "description TEXT NOT NULL, "
                "upvotes INTEGER DEFAULT 0, "
                "downvotes INTEGER DEFAULT 0)"
            )
            # Ensure columns exist if table was created previously without them
            cursor = conn.execute("PRAGMA table_info(posts)")
            cols = [row[1] for row in cursor.fetchall()]
            if "upvotes" not in cols:
                conn.execute("ALTER TABLE posts ADD COLUMN upvotes INTEGER DEFAULT 0")
            if "downvotes" not in cols:
                conn.execute("ALTER TABLE posts ADD COLUMN downvotes INTEGER DEFAULT 0")

            conn.execute(
                "CREATE TABLE IF NOT EXISTS post_votes ("
                "account_id INTEGER NOT NULL, "
                "post_id INTEGER NOT NULL, "
                "vote_type INTEGER NOT NULL, "
                "PRIMARY KEY (account_id, post_id))"
            )

    def add(self, post: Post) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "INSERT INTO posts (id, author_id, community_id, name, description, upvotes, downvotes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    post.id,
                    post.author_id,
                    post.community_id,
                    post.name,
                    post.description,
                    post.upvotes,
                    post.downvotes,
                ),
            )

    def find_by_id(self, post_id: int) -> Post | None:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, author_id, community_id, name, description, "
                "COALESCE(upvotes, 0), COALESCE(downvotes, 0) "
                "FROM posts WHERE id = ?",
                (post_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return Post(
                id=row[0],
                author_id=row[1],
                community_id=row[2],
                name=row[3],
                description=row[4],
                upvotes=row[5],
                downvotes=row[6],
            )

    def list_by_community(self, community_id: int) -> list[Post]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, author_id, community_id, name, description, "
                "COALESCE(upvotes, 0), COALESCE(downvotes, 0) "
                "FROM posts WHERE community_id = ? ORDER BY id DESC",
                (community_id,),
            )
            return [
                Post(
                    id=row[0],
                    author_id=row[1],
                    community_id=row[2],
                    name=row[3],
                    description=row[4],
                    upvotes=row[5],
                    downvotes=row[6],
                )
                for row in cursor.fetchall()
            ]

    def list_all(self) -> list[Post]:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT id, author_id, community_id, name, description, "
                "COALESCE(upvotes, 0), COALESCE(downvotes, 0) "
                "FROM posts ORDER BY id DESC"
            )
            return [
                Post(
                    id=row[0],
                    author_id=row[1],
                    community_id=row[2],
                    name=row[3],
                    description=row[4],
                    upvotes=row[5],
                    downvotes=row[6],
                )
                for row in cursor.fetchall()
            ]

    def update(self, post: Post) -> None:
        with self._db.connect() as conn:
            conn.execute(
                "UPDATE posts SET name = ?, description = ? WHERE id = ?",
                (post.name, post.description, post.id),
            )

    def delete(self, post_id: int) -> None:
        with self._db.connect() as conn:
            conn.execute("DELETE FROM post_votes WHERE post_id = ?", (post_id,))
            conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))

    def get_user_vote(self, account_id: int, post_id: int) -> int:
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT vote_type FROM post_votes WHERE account_id = ? AND post_id = ?",
                (account_id, post_id),
            )
            row = cursor.fetchone()
            return row[0] if row else 0

    def vote(self, account_id: int, post_id: int, direction: int) -> tuple[int, int, int]:
        """Apply a vote (1 for upvote, -1 for downvote, 0 to cancel).

        Toggles off if voting the same direction again.
        Returns (new_upvotes, new_downvotes, new_user_vote).
        """
        with self._db.connect() as conn:
            cursor = conn.execute(
                "SELECT vote_type FROM post_votes WHERE account_id = ? AND post_id = ?",
                (account_id, post_id),
            )
            row = cursor.fetchone()
            current_vote = row[0] if row else 0

            # Determine new vote state
            if direction == 0 or current_vote == direction:
                new_vote = 0
            else:
                new_vote = 1 if direction > 0 else -1

            # Calculate counter deltas
            up_delta = 0
            down_delta = 0

            # Revert old vote
            if current_vote == 1:
                up_delta -= 1
            elif current_vote == -1:
                down_delta -= 1

            # Apply new vote
            if new_vote == 1:
                up_delta += 1
            elif new_vote == -1:
                down_delta += 1

            # Update vote table
            if new_vote == 0:
                conn.execute(
                    "DELETE FROM post_votes WHERE account_id = ? AND post_id = ?",
                    (account_id, post_id),
                )
            else:
                conn.execute(
                    "INSERT INTO post_votes (account_id, post_id, vote_type) VALUES (?, ?, ?) "
                    "ON CONFLICT(account_id, post_id) DO UPDATE SET vote_type = excluded.vote_type",
                    (account_id, post_id, new_vote),
                )

            # Update cached integers in posts table
            conn.execute(
                "UPDATE posts SET "
                "upvotes = MAX(0, COALESCE(upvotes, 0) + ?), "
                "downvotes = MAX(0, COALESCE(downvotes, 0) + ?) "
                "WHERE id = ?",
                (up_delta, down_delta, post_id),
            )

            res = conn.execute(
                "SELECT COALESCE(upvotes, 0), COALESCE(downvotes, 0) FROM posts WHERE id = ?",
                (post_id,),
            ).fetchone()
            return (res[0], res[1], new_vote)
