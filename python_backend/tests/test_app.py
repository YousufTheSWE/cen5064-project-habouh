import pytest
from domain.account import Account
from domain.comment import Comment
from domain.community import Community
from domain.errors import InvalidUsernameError, PasswordTooShortError
from domain.post import Post


def test_create_account_and_verify_password():
    account = Account.create("testuser", "securepass123")
    assert account.username == "testuser"
    assert account.id > 0
    assert account.verify_password("securepass123") is True
    assert account.verify_password("wrongpassword") is False


def test_invalid_username():
    with pytest.raises(InvalidUsernameError):
        Account.create("invalid user!", "securepass123")


def test_password_too_short():
    with pytest.raises(PasswordTooShortError):
        Account.create("testuser", "short")


def test_entities_snowflake_ids():
    comm = Community.create(owner_id=123, name="Python", description="All about Python", picture="https://example.com/pic.png")
    post = Post.create(author_id=123, community_id=comm.id, name="Hello", description="First post")
    comment = Comment.create(author_id=123, post_id=post.id, description="Nice post")
    assert comm.id > 0 and post.id > 0 and comment.id > 0
    assert comm.owner_id == 123 and post.community_id == comm.id and comment.post_id == post.id
