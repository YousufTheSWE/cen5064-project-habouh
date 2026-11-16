from domain.errors import AuthenticationRequiredError
from fastapi import APIRouter, Header, Query
from presentation.auth_dependency import extract_token
from pydantic import BaseModel


class CreateAccountBody(BaseModel):
    username: str
    password: str


class LoginBody(BaseModel):
    username: str
    password: str


class UpdateUsernameBody(BaseModel):
    username: str


class UpdatePasswordBody(BaseModel):
    current_password: str
    new_password: str


def account_routes(service) -> APIRouter:
    router = APIRouter()

    @router.get("/check_username", status_code=200)
    def check_username(
        username: str = Query(...),
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        exclude_id = None
        if authorization or x_auth_code:
            try:
                token = extract_token(authorization, x_auth_code)
                exclude_id = service.get_account_id_from_token(token)
            except AuthenticationRequiredError:
                exclude_id = None
        available = service.is_username_available(username, exclude_account_id=exclude_id)
        return {"available": available, "username": username}

    @router.post("/create_account", status_code=201)
    def create_account(body: CreateAccountBody):
        res = service.create_account(body.username, body.password)
        return {
            "message": "Account created",
            "username": res["username"],
            "account_id": res["account_id"],
            "auth_token": res["auth_token"],
        }

    @router.post("/login", status_code=200)
    def login(body: LoginBody):
        res = service.login(body.username, body.password)
        return {
            "message": "Login successful",
            "username": res["username"],
            "account_id": res["account_id"],
            "auth_token": res["auth_token"],
        }

    @router.get("/me", status_code=200)
    def me(
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        account = service.get_account_by_token(token)
        return {"account_id": account.id, "username": account.username}

    @router.put("/me/username", status_code=200)
    def update_username(
        body: UpdateUsernameBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        account_id = service.get_account_id_from_token(token)
        new_username = service.update_username(account_id, body.username)
        return {"message": "Username updated", "username": new_username}

    @router.put("/me/password", status_code=200)
    def update_password(
        body: UpdatePasswordBody,
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        account_id = service.get_account_id_from_token(token)
        service.update_password(account_id, body.current_password, body.new_password)
        return {"message": "Password updated"}

    @router.post("/logout", status_code=200)
    def logout(
        authorization: str | None = Header(None),
        x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
    ):
        token = extract_token(authorization, x_auth_code)
        service.logout(token)
        return {"message": "Logged out"}

    return router
