from dataclasses import dataclass

from domain.errors import CommunityLimitExceededError, DomainError
from domain.snowflake import generate_snowflake

MAX_COMMUNITIES_PER_OWNER = 10


@dataclass(frozen=True)
class Community:
    id: int
    owner_id: int
    name: str
    description: str
    picture: str

    @staticmethod
    def validate_owner_community_count(current_count: int) -> None:
        if current_count >= MAX_COMMUNITIES_PER_OWNER:
            raise CommunityLimitExceededError()

    @staticmethod
    def create(
        owner_id: int,
        name: str,
        description: str,
        picture: str,
        community_id: int | None = None,
    ) -> "Community":
        clean_name = name.strip()
        if not clean_name:
            raise DomainError("Community name cannot be empty")
        resolved_id = community_id if community_id is not None else generate_snowflake()
        return Community(
            id=resolved_id,
            owner_id=owner_id,
            name=clean_name,
            description=description.strip(),
            picture=picture.strip(),
        )
