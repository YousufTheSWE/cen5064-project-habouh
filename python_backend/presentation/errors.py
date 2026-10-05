from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from domain.errors import DomainError, UsernameAlreadyExistsError

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(UsernameAlreadyExistsError)
    def conflict(request: Request, exc: UsernameAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": str(exc)})

    @app.exception_handler(DomainError)
    def domain_error(request: Request, exc: DomainError):
        return JSONResponse(status_code=400, content={"error": str(exc)})