from dataclasses import dataclass

from domain.errors import DomainError
from domain.snowflake import generate_snowflake


@dataclass(frozen=True)
class Post:
    id: int
    author_id: int
    community_id: int
    name: str
    description: str
    upvotes: int = 0
    downvotes: int = 0

    @staticmethod
    def create(
        author_id: int,
        community_id: int,
        name: str,
        description: str,
        post_id: int | None = None,
        upvotes: int = 0,
        downvotes: int = 0,
    ) -> "Post":
        clean_name = name.strip()
        if not clean_name:
            raise DomainError("Post name cannot be empty")
        resolved_id = post_id if post_id is not None else generate_snowflake()
        return Post(
            id=resolved_id,
            author_id=author_id,
            community_id=community_id,
            name=clean_name,
            description=description.strip(),
            upvotes=upvotes,
            downvotes=downvotes,
        )
