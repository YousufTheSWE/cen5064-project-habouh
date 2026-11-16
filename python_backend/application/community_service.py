from domain.community import Community
from domain.errors import (
    CommunityLimitExceededError,
    CommunityNotFoundError,
    DomainError,
    UnauthorizedActionError,
    UserNotFoundError,
)

MAX_COMMUNITIES_PER_OWNER = 10


class CommunityService:
    def __init__(self, repository):
        self._repository = repository

    def create_community(
        self,
        owner_id: int,
        name: str,
        description: str,
        picture: str,
    ) -> Community:
        owned_count = self._repository.count_by_owner(owner_id)
        if owned_count >= MAX_COMMUNITIES_PER_OWNER:
            raise CommunityLimitExceededError()
        community = Community.create(
            owner_id=owner_id,
            name=name,
            description=description,
            picture=picture,
        )
        self._repository.add(community)
        return community

    def get_community(self, community_id: int) -> Community:
        community = self._repository.find_by_id(community_id)
        if community is None:
            raise CommunityNotFoundError()
        return community

    def list_communities(self) -> list[Community]:
        return self._repository.list_all()

    def update_community(
        self,
        community_id: int,
        user_id: int,
        name: str,
        description: str,
        picture: str,
    ) -> Community:
        existing = self.get_community(community_id)
        if existing.owner_id != user_id:
            raise UnauthorizedActionError("Only the community owner can edit this community")
        updated = Community(
            id=existing.id,
            owner_id=existing.owner_id,
            name=name.strip(),
            description=description.strip(),
            picture=picture.strip(),
        )
        self._repository.update(updated)
        return updated

    def transfer_ownership(
        self,
        community_id: int,
        current_user_id: int,
        target_identifier: str,
        account_service,
    ) -> Community:
        existing = self.get_community(community_id)
        if existing.owner_id != current_user_id:
            raise UnauthorizedActionError("Only the community owner can transfer ownership")

        target_account = account_service.find_account_by_identifier(target_identifier)
        if target_account is None:
            raise UserNotFoundError("Target recipient user does not exist")

        if target_account.id == current_user_id:
            raise DomainError("You are already the owner of this community")

        recipient_owned_count = self._repository.count_by_owner(target_account.id)
        if recipient_owned_count >= MAX_COMMUNITIES_PER_OWNER:
            raise CommunityLimitExceededError(
                "Cannot transfer ownership: recipient already owns the maximum of 10 communities"
            )

        self._repository.transfer_ownership(community_id, target_account.id)
        return self.get_community(community_id)

    def delete_community(self, community_id: int, user_id: int) -> None:
        existing = self.get_community(community_id)
        if existing.owner_id != user_id:
            raise UnauthorizedActionError("Only the community owner can delete this community")
        self._repository.delete(community_id)
