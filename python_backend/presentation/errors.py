from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.errors import (
    AlreadyApprovedError,
    AuthenticationRequiredError,
    CommentNotFoundError,
    CommunityLimitExceededError,
    CommunityNotFoundError,
    DomainError,
    InvalidCredentialsError,
    PostNotFoundError,
    UnauthorizedActionError,
    UserBannedError,
    UsernameAlreadyExistsError,
    UserNotFoundError,
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(UsernameAlreadyExistsError)
    def conflict(request: Request, exc: UsernameAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    def unauthorized_credentials(request: Request, exc: InvalidCredentialsError):
        return JSONResponse(status_code=401, content={"error": str(exc)})

    @app.exception_handler(AuthenticationRequiredError)
    def authentication_required(request: Request, exc: AuthenticationRequiredError):
        return JSONResponse(status_code=401, content={"error": str(exc)})

    @app.exception_handler(UnauthorizedActionError)
    def forbidden(request: Request, exc: UnauthorizedActionError):
        return JSONResponse(status_code=403, content={"error": str(exc)})

    @app.exception_handler(UserBannedError)
    def user_banned(request: Request, exc: UserBannedError):
        return JSONResponse(status_code=403, content={"error": str(exc)})

    @app.exception_handler(AlreadyApprovedError)
    def already_approved(request: Request, exc: AlreadyApprovedError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(UserNotFoundError)
    def user_not_found(request: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(CommunityNotFoundError)
    def community_not_found(request: Request, exc: CommunityNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(PostNotFoundError)
    def post_not_found(request: Request, exc: PostNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(CommentNotFoundError)
    def comment_not_found(request: Request, exc: CommentNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(CommunityLimitExceededError)
    def limit_exceeded(request: Request, exc: CommunityLimitExceededError):
        return JSONResponse(status_code=400, content={"error": str(exc)})

    @app.exception_handler(DomainError)
    def domain_error(request: Request, exc: DomainError):
        return JSONResponse(status_code=400, content={"error": str(exc)})
