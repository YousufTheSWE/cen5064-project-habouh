class DomainError(Exception):
    """Base class for business rule failures."""


class InvalidUsernameError(DomainError):
    def __init__(self, *args):
        if not args:
            args = (
                (
                    "Account creation failed: username must contain only alphanumeric "
                    "characters and underscores, with at least one non-underscore character"
                ),
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


class AuthenticationRequiredError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("Authentication required: missing or invalid auth token",)
        super().__init__(*args)


class UserNotFoundError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("User not found",)
        super().__init__(*args)


class CommunityNotFoundError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("Community not found",)
        super().__init__(*args)


class PostNotFoundError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("Post not found",)
        super().__init__(*args)


class CommentNotFoundError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("Comment not found",)
        super().__init__(*args)


class UnauthorizedActionError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("You are not authorized to perform this action",)
        super().__init__(*args)


class CommunityLimitExceededError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("A user can be the owner of at most 10 communities",)
        super().__init__(*args)


class UserBannedError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("You are banned from this community",)
        super().__init__(*args)


class AlreadyApprovedError(DomainError):
    def __init__(self, *args):
        if not args:
            args = ("This content has already been approved and cannot be reported unless edited",)
        super().__init__(*args)
