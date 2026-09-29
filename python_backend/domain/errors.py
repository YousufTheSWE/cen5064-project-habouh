class DomainError(Exception):
    """Base class for business rule failures."""


class InvalidUsernameError(DomainError):
    def __init__(self):
        super().__init__(
            "Account creation failed: username must be at least 1 character "
            "and contain only alphanumeric characters"
        )


class PasswordTooShortError(DomainError):
    def __init__(self):
        super().__init__("Account creation failed: password is too short (minimum 8 characters)")


class UsernameAlreadyExistsError(DomainError):
    def __init__(self):
        super().__init__("Account creation failed: username already exists")