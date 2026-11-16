from domain.errors import AuthenticationRequiredError
from fastapi import APIRouter, Header, Query
from presentation.auth_dependency import extract_token
from pydantic import BaseModel


class CreatePostBody(BaseModel):
    community_id: int
    name: str
    description: str


class UpdatePostBody(BaseModel):
    name: str
    description: str


class VoteBody(BaseModel):
    direction: int  # 1 for upvote, -1 for downvote, 0 for cancel


def post_routes(service, account_service) -> APIRouter:
    router = APIRouter(prefix="/posts", tags=["posts"])

    def _resolve_user_id(authorization: str | None, x_auth_code: str | None) -> int | None:
        if not authorization and not x_auth_code:
            return None
        try:
            token = extract_token(authorization, x_auth_code)
            return account_service.get_account_id_from_token(token)
        except AuthenticationRequiredError:
            return None

    def _format_post(p, current_user_id: int | None = None):
        user_vote = service.get_user_vote(p.id, current_user_id) if current_user_id else 0
        return {
            "id": p.id,
            "author_id": p.author_id,
            "author_username": account_service.get_username_by_id(p.author_id),
            "community_id": p.community_id,
            "name": p.name,
            "description": p.description,
            "upvotes": p.upvotes,
            "downvotes": p.downvotes,
            "user_vote": user_vote,
        }

    @router.post("", status_code=201)
    def create_post(
        body: CreatePostBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        author_id = account_service.get_account_id_from_token(token)
        post = service.create_post(
            author_id=author_id,
            community_id=body.community_id,
            name=body.name,
            description=body.description,
        )
        return {
            "message": "Post created",
            "post": _format_post(post, author_id),
        }

    @router.get("", status_code=200)
    def list_posts(
        community_id: int | None = Query(None),
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        current_user_id = _resolve_user_id(authorization, x_auth_code)
        posts = service.list_posts(community_id=community_id)
        return [_format_post(p, current_user_id) for p in posts]

    @router.get("/{post_id}", status_code=200)
    def get_post(
        post_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        current_user_id = _resolve_user_id(authorization, x_auth_code)
        p = service.get_post(post_id)
        return _format_post(p, current_user_id)

    @router.put("/{post_id}", status_code=200)
    def update_post(
        post_id: int,
        body: UpdatePostBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        p = service.update_post(
            post_id=post_id,
            user_id=user_id,
            name=body.name,
            description=body.description,
        )
        return {
            "message": "Post updated",
            "post": _format_post(p, user_id),
        }

    @router.post("/{post_id}/vote", status_code=200)
    def vote_post(
        post_id: int,
        body: VoteBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        result = service.vote(post_id, user_id, body.direction)
        return {
            "message": "Vote recorded",
            "upvotes": result["upvotes"],
            "downvotes": result["downvotes"],
            "user_vote": result["user_vote"],
        }

    @router.delete("/{post_id}", status_code=200)
    def delete_post(
        post_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        service.delete_post(post_id, user_id)
        return {"message": "Post deleted"}

    return router
