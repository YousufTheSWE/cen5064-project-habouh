import uvicorn
from application.account_service import AccountService
from application.comment_service import CommentService
from application.community_service import CommunityService
from application.post_service import PostService
from config import load_env
from data.account_repository import SqliteAccountRepository
from data.comment_repository import SqliteCommentRepository
from data.community_repository import SqliteCommunityRepository
from data.database import Database
from data.post_repository import SqlitePostRepository
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from presentation.account_routes import account_routes
from presentation.comment_routes import comment_routes
from presentation.community_routes import community_routes
from presentation.errors import register_error_handlers
from presentation.post_routes import post_routes


def create_app() -> FastAPI:
    config = load_env()
    database = Database(config["DATABASE_PATH"])

    account_repo = SqliteAccountRepository(database)
    community_repo = SqliteCommunityRepository(database)
    post_repo = SqlitePostRepository(database)
    comment_repo = SqliteCommentRepository(database)

    account_service = AccountService(account_repo)
    community_service = CommunityService(community_repo)
    post_service = PostService(post_repo, community_repository=community_repo)
    comment_service = CommentService(comment_repo, post_repository=post_repo)

    app = FastAPI(title="PostClient API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)

    app.include_router(account_routes(account_service))
    app.include_router(community_routes(community_service, account_service))
    app.include_router(post_routes(post_service, account_service))
    app.include_router(comment_routes(comment_service, account_service))

    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)
