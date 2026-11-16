import pytest

from application.account_service import AccountService
from data.account_repository import SqliteAccountRepository
from data.database import Database
from domain.errors import (
    AuthenticationRequiredError,
    InvalidCredentialsError,
    PasswordTooShortError,
    UsernameAlreadyExistsError,
)


@pytest.fixture
def account_service(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    repo = SqliteAccountRepository(db)
    return AccountService(repo)


def test_register_and_login_flow(account_service):
    res = account_service.create_account("alice", "password123")
    token = res["auth_token"]
    assert token is not None
    user_id = account_service.get_account_id_from_token(token)
    assert user_id == res["account_id"]

    login_res = account_service.login("alice", "password123")
    login_token = login_res["auth_token"]
    assert login_token is not None
    assert account_service.get_account_id_from_token(login_token) == user_id


def test_duplicate_username_fails(account_service):
    account_service.create_account("duplicate_user", "password123")
    with pytest.raises(UsernameAlreadyExistsError):
        account_service.create_account("duplicate_user", "differentpass")


def test_invalid_login_credentials(account_service):
    account_service.create_account("bob", "password123")
    with pytest.raises(InvalidCredentialsError):
        account_service.login("bob", "wrongpassword")
    with pytest.raises(InvalidCredentialsError):
        account_service.login("nonexistent", "password123")


def test_invalid_token(account_service):
    with pytest.raises(AuthenticationRequiredError):
        account_service.get_account_id_from_token("fake-token-123")


def test_check_username_availability(account_service):
    assert account_service.is_username_available("newuser") is True
    res = account_service.create_account("takenuser", "password123")
    user_id = res["account_id"]
    assert account_service.is_username_available("takenuser") is False
    assert account_service.is_username_available("takenuser", exclude_account_id=user_id) is True


def test_update_username(account_service):
    res = account_service.create_account("oldname", "password123")
    user_id = res["account_id"]

    updated_name = account_service.update_username(user_id, "newname")
    assert updated_name == "newname"
    assert account_service.get_username_by_id(user_id) == "newname"

    # Cannot update to already taken username
    account_service.create_account("charlie", "password123")
    with pytest.raises(UsernameAlreadyExistsError):
        account_service.update_username(user_id, "charlie")


def test_update_password(account_service):
    res = account_service.create_account("passuser", "oldpassword123")
    user_id = res["account_id"]

    # Wrong current password fails
    with pytest.raises(InvalidCredentialsError):
        account_service.update_password(user_id, "wrongpass", "newpassword123")

    # Short new password fails
    with pytest.raises(PasswordTooShortError):
        account_service.update_password(user_id, "oldpassword123", "short")

    # Success updates password
    account_service.update_password(user_id, "oldpassword123", "newpassword123")
    # Login works with new password
    login_res = account_service.login("passuser", "newpassword123")
    assert account_service.get_account_id_from_token(login_res["auth_token"]) == user_id


def test_find_account_by_identifier(account_service):
    res = account_service.create_account("targetuser", "password123")
    user_id = res["account_id"]

    # Lookup by username
    by_name = account_service.find_account_by_identifier("targetuser")
    assert by_name is not None
    assert by_name.id == user_id

    # Lookup by numeric ID string
    by_id = account_service.find_account_by_identifier(str(user_id))
    assert by_id is not None
    assert by_id.username == "targetuser"

    # Nonexistent identifier returns None
    assert account_service.find_account_by_identifier("nobody") is None
