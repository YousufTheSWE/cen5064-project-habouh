from domain.community import Community
from domain.errors import (
    CommunityNotFoundError,
    DomainError,
    UnauthorizedActionError,
    UserNotFoundError,
)


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
        Community.validate_owner_community_count(owned_count)
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
        Community.validate_owner_community_count(recipient_owned_count)

        self._repository.transfer_ownership(community_id, target_account.id)
        return self.get_community(community_id)

    def delete_community(self, community_id: int, user_id: int) -> None:
        existing = self.get_community(community_id)
        if existing.owner_id != user_id:
            raise UnauthorizedActionError("Only the community owner can delete this community")
        self._repository.delete(community_id)

    # Moderator Designation (Owner Only)
    def add_moderator(
        self,
        community_id: int,
        current_user_id: int,
        target_identifier: str,
        account_service,
    ) -> dict:
        community = self.get_community(community_id)
        if community.owner_id != current_user_id:
            raise UnauthorizedActionError("Only the community owner can designate moderators")

        target_account = account_service.find_account_by_identifier(target_identifier)
        if target_account is None:
            raise UserNotFoundError("User not found")

        if target_account.id == community.owner_id:
            raise DomainError("Community owner already has all moderation permissions")

        self._repository.add_moderator(community_id, target_account.id)
        return {
            "community_id": community_id,
            "account_id": target_account.id,
            "username": target_account.username,
        }

    def remove_moderator(
        self,
        community_id: int,
        current_user_id: int,
        target_account_id: int,
    ) -> None:
        community = self.get_community(community_id)
        if community.owner_id != current_user_id:
            raise UnauthorizedActionError("Only the community owner can remove moderators")
        self._repository.remove_moderator(community_id, target_account_id)

    def list_moderators(self, community_id: int, account_service) -> list[dict]:
        self.get_community(community_id)
        mod_ids = self._repository.list_moderators(community_id)
        return [
            {
                "account_id": uid,
                "username": account_service.get_username_by_id(uid),
            }
            for uid in mod_ids
        ]

    def is_moderator_or_owner(self, community_id: int, user_id: int) -> bool:
        community = self.get_community(community_id)
        if community.owner_id == user_id:
            return True
        return self._repository.is_moderator(community_id, user_id)

    # Banned User Management (Owner & Moderators)
    def ban_user(
        self,
        community_id: int,
        current_user_id: int,
        target_identifier: str,
        account_service,
    ) -> dict:
        if not self.is_moderator_or_owner(community_id, current_user_id):
            raise UnauthorizedActionError("Only moderators and the owner can ban users")

        community = self.get_community(community_id)
        target_account = account_service.find_account_by_identifier(target_identifier)
        if target_account is None:
            raise UserNotFoundError("User not found")

        if target_account.id == community.owner_id:
            raise DomainError("The community owner cannot be banned")

        self._repository.ban_user(community_id, target_account.id, current_user_id)
        # If user was a moderator, revoke moderator status
        self._repository.remove_moderator(community_id, target_account.id)

        return {
            "community_id": community_id,
            "account_id": target_account.id,
            "username": target_account.username,
        }

    def unban_user(
        self,
        community_id: int,
        current_user_id: int,
        target_account_id: int,
    ) -> None:
        if not self.is_moderator_or_owner(community_id, current_user_id):
            raise UnauthorizedActionError("Only moderators and the owner can unban users")
        self._repository.unban_user(community_id, target_account_id)

    def list_banned(self, community_id: int, current_user_id: int, account_service) -> list[dict]:
        if not self.is_moderator_or_owner(community_id, current_user_id):
            raise UnauthorizedActionError("Only moderators and the owner can view banned users")
        banned_rows = self._repository.list_banned(community_id)
        return [
            {
                "account_id": r["account_id"],
                "username": account_service.get_username_by_id(r["account_id"]),
                "banned_by_id": r["banned_by_id"],
                "banned_by_username": account_service.get_username_by_id(r["banned_by_id"]),
                "created_at": r["created_at"],
            }
            for r in banned_rows
        ]

    def is_banned(self, community_id: int, user_id: int) -> bool:
        return self._repository.is_banned(community_id, user_id)
