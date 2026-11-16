from fastapi import APIRouter, Header
from pydantic import BaseModel

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


def community_routes(service, account_service) -> APIRouter:
    router = APIRouter(prefix="/communities", tags=["communities"])

    def _format_community(c):
        return {
            "id": c.id,
            "owner_id": c.owner_id,
            "owner_username": account_service.get_username_by_id(c.owner_id),
            "name": c.name,
            "description": c.description,
            "picture": c.picture,
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
            "community": _format_community(community),
        }

    @router.get("", status_code=200)
    def list_communities():
        communities = service.list_communities()
        return [_format_community(c) for c in communities]

    @router.get("/{community_id}", status_code=200)
    def get_community(community_id: int):
        c = service.get_community(community_id)
        return _format_community(c)

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
            "community": _format_community(c),
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
            "community": _format_community(c),
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

    return router
