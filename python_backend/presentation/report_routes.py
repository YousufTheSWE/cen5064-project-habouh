from fastapi import APIRouter, Header
from pydantic import BaseModel

from presentation.auth_dependency import extract_token


class TargetBody(BaseModel):
    target: str


def report_routes(report_service, account_service) -> APIRouter:
    router = APIRouter(tags=["reports"])

    @router.post("/posts/{post_id}/report", status_code=200)
    def report_post(
        post_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        report_service.report_post(user_id, post_id)
        return {"message": "Post reported successfully"}

    @router.post("/comments/{comment_id}/report", status_code=200)
    def report_comment(
        comment_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        report_service.report_comment(user_id, comment_id)
        return {"message": "Comment reported successfully"}

    @router.get("/communities/{community_id}/reports", status_code=200)
    def list_reports(
        community_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        return report_service.list_reports(community_id, user_id, account_service)

    @router.post("/communities/{community_id}/reports/{target_type}/{target_id}/approve", status_code=200)
    def approve_report(
        community_id: int,
        target_type: str,
        target_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        report_service.approve_item(community_id, user_id, target_type, target_id)
        return {"message": f"{target_type.capitalize()} approved"}

    @router.delete("/communities/{community_id}/reports/{target_type}/{target_id}", status_code=200)
    def delete_reported(
        community_id: int,
        target_type: str,
        target_id: int,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        user_id = account_service.get_account_id_from_token(token)
        report_service.delete_reported_item(community_id, user_id, target_type, target_id)
        return {"message": f"{target_type.capitalize()} deleted"}

    return router
