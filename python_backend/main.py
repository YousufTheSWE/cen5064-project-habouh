import uvicorn
from fastapi import FastAPI

from application.account_service import AccountService
from config import load_env
from data.account_repository import SqliteAccountRepository
from data.database import Database
from presentation.account_routes import account_routes
from presentation.errors import register_error_handlers


def create_app() -> FastAPI:
    config = load_env()
    database = Database(config["DATABASE_PATH"])

    account_service = AccountService(SqliteAccountRepository(database))

    app = FastAPI()
    register_error_handlers(app)
    app.include_router(account_routes(account_service))
    # app.include_router(post_routes(post_service), prefix="/v1")
    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)