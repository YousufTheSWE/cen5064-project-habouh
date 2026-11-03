class DomainError(Exception):
    """Base class for business rule failures."""


class InvalidUsernameError(DomainError):
    def __init__(self, *args):
        if not args:
            args = (
                ("Account creation failed: username must be at least 1 character "
                "and contain only alphanumeric characters"),
            )
        super().__init__(*args)


class PasswordTooShortError(DomainError):
    def __init__(self, *args):
        if not args:
            args = (
                "Account creation failed: password is too short (minimum 8 characters)",
            )
        super().__init__(*args)


class UsernameAlreadyExistsError(DomainError):
    def __init__(self, *args):
        if not args:
            args = (
                "Account creation failed: username already exists",
            )
        super().__init__(*args)


class InvalidCredentialsError(DomainError):
    def __init__(self, *args):
        if not args:
            args = (
                "Login failed: invalid username or password",
            )
        super().__init__(*args)
