from fastapi import APIRouter, Header
from pydantic import BaseModel

from domain.errors import AuthenticationRequiredError
from presentation.auth_dependency import extract_token


class CreateCommunityBody(BaseModel):
    name: str
    description: str
    picture: str


class UpdateCommunityBody(BaseModel):
    name: str
    description: str
    picture: str


class TransferOwnershipBody(BaseModel):
    target: str


class TargetUserBody(BaseModel):
    target: str


def community_routes(service, account_service) -> APIRouter:
    router = APIRouter(prefix="/communities", tags=["communities"])

    def _resolve_user_id(authorization: str | None, x_auth_code: str | None) -> int | None:
        if not authorization and not x_auth_code:
            return None
        try:
            token = extract_token(authorization, x_auth_code)
            return account_service.get_account_id_from_token(token)
        except AuthenticationRequiredError:
            return None

    def _format_community(c, current_user_id: int | None = None):
        is_owner = current_user_id == c.owner_id if current_user_id else False
        is_mod = service.is_moderator_or_owner(c.id, current_user_id) if current_user_id else False
        is_banned = service.is_banned(c.id, current_user_id) if current_user_id else False

        return {
            "id": c.id,
            "owner_id": c.owner_id,
            "owner_username": account_service.get_username_by_id(c.owner_id),
            "name": c.name,
            "description": c.description,
            "picture": c.picture,
            "is_owner": is_owner,
            "is_moderator": is_mod,
            "is_banned": is_banned,
        }

    @router.post("", status_code=201)
    def create_community(
        body: CreateCommunityBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        owner_id = account_service.get_account_id_from_token(token)
        community = service.create_community(
            owner_id=owner_id,
            name=body.name,
            description=body.description,
            picture=body.picture,
        )
        return {
            "message": "Community created",
            "community": _format_community(community, owner_id),
        }

    @router.get("", status_code=200)
    def list_communities(
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        user_id = _resolve_user_id(authorization, x_auth_code)
        communities = service.list_communities()
        return [_format_community(c, user_id) for c in communities]

    @router.get("/{community_id}", status_code=200)
    def get_community(
        community_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        user_id = _resolve_user_id(authorization, x_auth_code)
        c = service.get_community(community_id)
        return _format_community(c, user_id)

    @router.put("/{community_id}", status_code=200)
    def update_community(
        community_id: int,
        body: UpdateCommunityBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        c = service.update_community(
            community_id=community_id,
            user_id=user_id,
            name=body.name,
            description=body.description,
            picture=body.picture,
        )
        return {
            "message": "Community updated",
            "community": _format_community(c, user_id),
        }

    @router.post("/{community_id}/transfer_ownership", status_code=200)
    def transfer_ownership(
        community_id: int,
        body: TransferOwnershipBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        current_user_id = account_service.get_account_id_from_token(token)
        c = service.transfer_ownership(
            community_id=community_id,
            current_user_id=current_user_id,
            target_identifier=body.target,
            account_service=account_service,
        )
        return {
            "message": "Community ownership transferred",
            "community": _format_community(c, current_user_id),
        }

    @router.delete("/{community_id}", status_code=200)
    def delete_community(
        community_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        service.delete_community(community_id, user_id)
        return {"message": "Community deleted"}

    # Moderator Routes
    @router.get("/{community_id}/moderators", status_code=200)
    def list_moderators(community_id: int):
        return service.list_moderators(community_id, account_service)

    @router.post("/{community_id}/moderators", status_code=201)
    def add_moderator(
        community_id: int,
        body: TargetUserBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        mod = service.add_moderator(community_id, user_id, body.target, account_service)
        return {"message": "Moderator added", "moderator": mod}

    @router.delete("/{community_id}/moderators/{target_account_id}", status_code=200)
    def remove_moderator(
        community_id: int,
        target_account_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        service.remove_moderator(community_id, user_id, target_account_id)
        return {"message": "Moderator removed"}

    # Banned User Routes
    @router.get("/{community_id}/banned", status_code=200)
    def list_banned(
        community_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        return service.list_banned(community_id, user_id, account_service)

    @router.post("/{community_id}/banned", status_code=201)
    def ban_user(
        community_id: int,
        body: TargetUserBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        banned = service.ban_user(community_id, user_id, body.target, account_service)
        return {"message": "User banned", "banned": banned}

    @router.delete("/{community_id}/banned/{target_account_id}", status_code=200)
    def unban_user(
        community_id: int,
        target_account_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        service.unban_user(community_id, user_id, target_account_id)
        return {"message": "User unbanned"}

    return router
