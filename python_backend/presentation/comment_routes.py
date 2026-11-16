from domain.errors import AuthenticationRequiredError
from fastapi import APIRouter, Header, Query
from presentation.auth_dependency import extract_token
from pydantic import BaseModel


class CreateCommentBody(BaseModel):
    post_id: int
    description: str


class UpdateCommentBody(BaseModel):
    description: str


class VoteBody(BaseModel):
    direction: int


def comment_routes(service, account_service) -> APIRouter:
    router = APIRouter(prefix="/comments", tags=["comments"])

    def _resolve_user_id(authorization: str | None, x_auth_code: str | None) -> int | None:
        if not authorization and not x_auth_code:
            return None
        try:
            token = extract_token(authorization, x_auth_code)
            return account_service.get_account_id_from_token(token)
        except AuthenticationRequiredError:
            return None

    def _format_comment(c, current_user_id: int | None = None):
        user_vote = service.get_user_vote(c.id, current_user_id) if current_user_id else 0
        return {
            "id": c.id,
            "author_id": c.author_id,
            "author_username": account_service.get_username_by_id(c.author_id),
            "post_id": c.post_id,
            "description": c.description,
            "upvotes": c.upvotes,
            "downvotes": c.downvotes,
            "user_vote": user_vote,
        }

    @router.post("", status_code=201)
    def create_comment(
        body: CreateCommentBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        author_id = account_service.get_account_id_from_token(token)
        comment = service.create_comment(
            author_id=author_id,
            post_id=body.post_id,
            description=body.description,
        )
        return {
            "message": "Comment created",
            "comment": _format_comment(comment, author_id),
        }

    @router.get("", status_code=200)
    def list_comments(
        post_id: int = Query(...),
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        current_user_id = _resolve_user_id(authorization, x_auth_code)
        comments = service.list_comments(post_id=post_id)
        return [_format_comment(c, current_user_id) for c in comments]

    @router.get("/{comment_id}", status_code=200)
    def get_comment(
        comment_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        current_user_id = _resolve_user_id(authorization, x_auth_code)
        c = service.get_comment(comment_id)
        return _format_comment(c, current_user_id)

    @router.put("/{comment_id}", status_code=200)
    def update_comment(
        comment_id: int,
        body: UpdateCommentBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        c = service.update_comment(
            comment_id=comment_id,
            user_id=user_id,
            description=body.description,
        )
        return {
            "message": "Comment updated",
            "comment": _format_comment(c, user_id),
        }

    @router.post("/{comment_id}/vote", status_code=200)
    def vote_comment(
        comment_id: int,
        body: VoteBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        result = service.vote(comment_id, user_id, body.direction)
        return {
            "message": "Vote recorded",
            "upvotes": result["upvotes"],
            "downvotes": result["downvotes"],
            "user_vote": result["user_vote"],
        }

    @router.delete("/{comment_id}", status_code=200)
    def delete_comment(
        comment_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        service.delete_comment(comment_id, user_id)
        return {"message": "Comment deleted"}

    return router
