from fastapi import APIRouter
from pydantic import BaseModel


class CreateAccountBody(BaseModel):
    username: str
    password: str


class LoginBody(BaseModel):
    username: str
    password: str


def account_routes(service) -> APIRouter:
    router = APIRouter()

    @router.post("/create_account", status_code=201)
    def create_account(body: CreateAccountBody):
        username = service.create_account(body.username, body.password)
        return {"message": "Account created", "username": username}

    @router.post("/login", status_code=200)
    def login(body: LoginBody):
        username = service.login(body.username, body.password)
        return {"message": "Login successful", "username": username}

    return router