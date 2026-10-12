import pytest

from domain.account import Account
from domain.errors import InvalidUsernameError, PasswordTooShortError


def test_create_account_and_verify_password():
    account = Account.create("testuser", "securepass123")
    assert account.username == "testuser"
    assert account.verify_password("securepass123") is True
    assert account.verify_password("wrongpassword") is False


def test_invalid_username():
    with pytest.raises(InvalidUsernameError):
        Account.create("invalid user!", "securepass123")


def test_password_too_short():
    with pytest.raises(PasswordTooShortError):
        Account.create("testuser", "short")