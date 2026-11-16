from dataclasses import dataclass

from domain.errors import DomainError
from domain.snowflake import generate_snowflake


@dataclass(frozen=True)
class Comment:
    id: int
    author_id: int
    post_id: int
    description: str
    upvotes: int = 0
    downvotes: int = 0

    @staticmethod
    def create(
        author_id: int,
        post_id: int,
        description: str,
        comment_id: int | None = None,
        upvotes: int = 0,
        downvotes: int = 0,
    ) -> "Comment":
        clean_desc = description.strip()
        if not clean_desc:
            raise DomainError("Comment description cannot be empty")
        resolved_id = comment_id if comment_id is not None else generate_snowflake()
        return Comment(
            id=resolved_id,
            author_id=author_id,
            post_id=post_id,
            description=clean_desc,
            upvotes=upvotes,
            downvotes=downvotes,
        )
