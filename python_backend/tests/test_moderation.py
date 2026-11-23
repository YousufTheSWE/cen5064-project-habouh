import pytest

from application.account_service import AccountService
from application.comment_service import CommentService
from application.community_service import CommunityService
from application.post_service import PostService
from data.account_repository import SqliteAccountRepository
from data.comment_repository import SqliteCommentRepository
from data.community_repository import SqliteCommunityRepository
from data.database import Database
from data.post_repository import SqlitePostRepository
from domain.errors import (
    DomainError,
    PostNotFoundError,
    UnauthorizedActionError,
    UserBannedError,
)


@pytest.fixture
def mod_env(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    account_repo = SqliteAccountRepository(db)
    comm_repo = SqliteCommunityRepository(db)
    post_repo = SqlitePostRepository(db)
    comment_repo = SqliteCommentRepository(db)

    account_svc = AccountService(account_repo)
    comm_svc = CommunityService(comm_repo)
    post_svc = PostService(post_repo, community_repository=comm_repo)
    comment_svc = CommentService(comment_repo, post_repository=post_repo, community_repository=comm_repo)

    owner_res = account_svc.create_account("owner_user", "password123")
    mod_res = account_svc.create_account("mod_user", "password123")
    regular_res = account_svc.create_account("regular_user", "password123")
    bad_res = account_svc.create_account("troublemaker", "password123")

    owner_id = owner_res["account_id"]
    mod_id = mod_res["account_id"]
    regular_id = regular_res["account_id"]
    bad_id = bad_res["account_id"]

    comm = comm_svc.create_community(owner_id, "ModTalk", "Community with moderation", "https://pic.png")

    return {
        "comm_svc": comm_svc,
        "account_svc": account_svc,
        "post_svc": post_svc,
        "comment_svc": comment_svc,
        "comm_id": comm.id,
        "owner_id": owner_id,
        "mod_id": mod_id,
        "regular_id": regular_id,
        "bad_id": bad_id,
    }


def test_designate_and_remove_moderator(mod_env):
    comm_svc = mod_env["comm_svc"]
    account_svc = mod_env["account_svc"]
    comm_id = mod_env["comm_id"]
    owner_id = mod_env["owner_id"]
    mod_id = mod_env["mod_id"]
    regular_id = mod_env["regular_id"]

    # Regular user cannot designate moderators
    with pytest.raises(UnauthorizedActionError):
        comm_svc.add_moderator(comm_id, current_user_id=regular_id, target_identifier="mod_user", account_service=account_svc)

    # Owner designates moderator by username
    added = comm_svc.add_moderator(comm_id, current_user_id=owner_id, target_identifier="mod_user", account_service=account_svc)
    assert added["account_id"] == mod_id
    assert comm_svc.is_moderator_or_owner(comm_id, mod_id) is True

    # List moderators
    mods = comm_svc.list_moderators(comm_id, account_svc)
    assert len(mods) == 1
    assert mods[0]["account_id"] == mod_id

    # Owner removes moderator
    comm_svc.remove_moderator(comm_id, current_user_id=owner_id, target_account_id=mod_id)
    assert comm_svc.is_moderator_or_owner(comm_id, mod_id) is False


def test_ban_and_unban_user(mod_env):
    comm_svc = mod_env["comm_svc"]
    account_svc = mod_env["account_svc"]
    comm_id = mod_env["comm_id"]
    owner_id = mod_env["owner_id"]
    mod_id = mod_env["mod_id"]
    bad_id = mod_env["bad_id"]

    # Designate mod_id as moderator
    comm_svc.add_moderator(comm_id, owner_id, "mod_user", account_svc)

    # Moderator bans bad_user by username
    banned = comm_svc.ban_user(comm_id, current_user_id=mod_id, target_identifier="troublemaker", account_service=account_svc)
    assert banned["account_id"] == bad_id
    assert comm_svc.is_banned(comm_id, bad_id) is True

    # Owner cannot be banned
    with pytest.raises(DomainError, match="owner cannot be banned"):
        comm_svc.ban_user(comm_id, current_user_id=mod_id, target_identifier="owner_user", account_service=account_svc)

    # List banned
    banned_list = comm_svc.list_banned(comm_id, current_user_id=mod_id, account_service=account_svc)
    assert len(banned_list) == 1
    assert banned_list[0]["account_id"] == bad_id

    # Moderator unbans bad_user
    comm_svc.unban_user(comm_id, current_user_id=mod_id, target_account_id=bad_id)
    assert comm_svc.is_banned(comm_id, bad_id) is False


def test_banned_user_cannot_post_or_comment(mod_env):
    comm_svc = mod_env["comm_svc"]
    account_svc = mod_env["account_svc"]
    post_svc = mod_env["post_svc"]
    comment_svc = mod_env["comment_svc"]
    comm_id = mod_env["comm_id"]
    owner_id = mod_env["owner_id"]
    bad_id = mod_env["bad_id"]

    # Owner creates a post
    post = post_svc.create_post(owner_id, comm_id, "Welcome", "Rules of the community")

    # Ban troublemaker
    comm_svc.ban_user(comm_id, current_user_id=owner_id, target_identifier="troublemaker", account_service=account_svc)

    # Banned user cannot create post
    with pytest.raises(UserBannedError):
        post_svc.create_post(bad_id, comm_id, "Spam Title", "Spam content")

    # Banned user cannot comment on post in this community
    with pytest.raises(UserBannedError):
        comment_svc.create_comment(bad_id, post.id, "Spam comment")


def test_moderator_can_delete_reported_or_bad_post(mod_env):
    comm_svc = mod_env["comm_svc"]
    account_svc = mod_env["account_svc"]
    post_svc = mod_env["post_svc"]
    comm_id = mod_env["comm_id"]
    owner_id = mod_env["owner_id"]
    mod_id = mod_env["mod_id"]
    regular_id = mod_env["regular_id"]

    # Regular user creates a post
    post = post_svc.create_post(regular_id, comm_id, "Regular Post", "Body")

    # Designate mod_user
    comm_svc.add_moderator(comm_id, owner_id, "mod_user", account_svc)

    # Moderator deletes post created by another user
    post_svc.delete_post(post.id, user_id=mod_id)
    with pytest.raises(PostNotFoundError):
        post_svc.get_post(post.id)
