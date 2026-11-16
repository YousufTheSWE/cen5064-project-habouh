from fastapi import Header

from domain.errors import AuthenticationRequiredError


def extract_token(
    authorization: str | None = Header(None),
    x_auth_code: str | None = Header(None, alias="X-Auth-Code"),
) -> str:
    token = None
    if authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        elif len(parts) == 1:
            token = parts[0]
    elif x_auth_code:
        token = x_auth_code.strip()

    if not token:
        raise AuthenticationRequiredError()
    return token
