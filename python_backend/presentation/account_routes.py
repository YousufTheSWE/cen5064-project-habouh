from fastapi import APIRouter
from pydantic import BaseModel


class CreateAccountBody(BaseModel):
    username: str
    password: str


def account_routes(service) -> APIRouter:
    router = APIRouter()

    @router.post("/create_account", status_code=201)
    def create_account(body: CreateAccountBody):
        username = service.create_account(body.username, body.password)
        return {"message": "Account created", "username": username}

    return router