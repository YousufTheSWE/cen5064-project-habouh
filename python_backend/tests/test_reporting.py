import pytest

from application.account_service import AccountService
from application.comment_service import CommentService
from application.community_service import CommunityService
from application.post_service import PostService
from application.report_service import ReportService
from data.account_repository import SqliteAccountRepository
from data.comment_repository import SqliteCommentRepository
from data.community_repository import SqliteCommunityRepository
from data.database import Database
from data.post_repository import SqlitePostRepository
from data.report_repository import SqliteReportRepository
from domain.errors import (
    AlreadyApprovedError,
    PostNotFoundError,
    UnauthorizedActionError,
    UserBannedError,
)


@pytest.fixture
def rep_env(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    account_repo = SqliteAccountRepository(db)
    comm_repo = SqliteCommunityRepository(db)
    post_repo = SqlitePostRepository(db)
    comment_repo = SqliteCommentRepository(db)
    report_repo = SqliteReportRepository(db)

    account_svc = AccountService(account_repo)
    comm_svc = CommunityService(comm_repo)
    post_svc = PostService(post_repo, community_repository=comm_repo)
    comment_svc = CommentService(comment_repo, post_repository=post_repo, community_repository=comm_repo)
    report_svc = ReportService(
        report_repository=report_repo,
        post_repository=post_repo,
        comment_repository=comment_repo,
        community_repository=comm_repo,
    )

    owner_res = account_svc.create_account("owner_rep", "password123")
    mod_res = account_svc.create_account("mod_rep", "password123")
    user1_res = account_svc.create_account("user_rep1", "password123")
    user2_res = account_svc.create_account("user_rep2", "password123")
    bad_res = account_svc.create_account("banned_rep", "password123")

    owner_id = owner_res["account_id"]
    mod_id = mod_res["account_id"]
    user1_id = user1_res["account_id"]
    user2_id = user2_res["account_id"]
    bad_id = bad_res["account_id"]

    comm = comm_svc.create_community(owner_id, "ReportCommunity", "desc", "https://pic.png")
    comm_svc.add_moderator(comm.id, owner_id, "mod_rep", account_svc)
    comm_svc.ban_user(comm.id, owner_id, "banned_rep", account_svc)

    post = post_svc.create_post(user1_id, comm.id, "Target Post", "Some post content")
    comment = comment_svc.create_comment(user1_id, post.id, "Some comment content")

    return {
        "account_svc": account_svc,
        "comm_svc": comm_svc,
        "post_svc": post_svc,
        "comment_svc": comment_svc,
        "report_svc": report_svc,
        "comm_id": comm.id,
        "owner_id": owner_id,
        "mod_id": mod_id,
        "user1_id": user1_id,
        "user2_id": user2_id,
        "bad_id": bad_id,
        "post": post,
        "comment": comment,
    }


def test_report_post_and_comment(rep_env):
    report_svc = rep_env["report_svc"]
    account_svc = rep_env["account_svc"]
    comm_id = rep_env["comm_id"]
    mod_id = rep_env["mod_id"]
    user2_id = rep_env["user2_id"]
    post = rep_env["post"]
    comment = rep_env["comment"]

    # user2 reports post and comment
    report_svc.report_post(user_id=user2_id, post_id=post.id)
    report_svc.report_comment(user_id=user2_id, comment_id=comment.id)

    # Moderator can list reports
    reports = report_svc.list_reports(comm_id, user_id=mod_id, account_service=account_svc)
    assert len(reports) == 2

    post_reports = [r for r in reports if r["target_type"] == "post"]
    comment_reports = [r for r in reports if r["target_type"] == "comment"]

    assert len(post_reports) == 1
    assert post_reports[0]["content"] == "Some post content"
    assert post_reports[0]["reporters"][0]["username"] == "user_rep2"

    assert len(comment_reports) == 1
    assert comment_reports[0]["content"] == "Some comment content"
    assert comment_reports[0]["reporters"][0]["username"] == "user_rep2"


def test_banned_user_cannot_report(rep_env):
    report_svc = rep_env["report_svc"]
    bad_id = rep_env["bad_id"]
    post = rep_env["post"]
    comment = rep_env["comment"]

    with pytest.raises(UserBannedError):
        report_svc.report_post(user_id=bad_id, post_id=post.id)

    with pytest.raises(UserBannedError):
        report_svc.report_comment(user_id=bad_id, comment_id=comment.id)


def test_non_moderator_cannot_view_report_log(rep_env):
    report_svc = rep_env["report_svc"]
    account_svc = rep_env["account_svc"]
    comm_id = rep_env["comm_id"]
    user1_id = rep_env["user1_id"]

    with pytest.raises(UnauthorizedActionError):
        report_svc.list_reports(comm_id, user_id=user1_id, account_service=account_svc)


def test_approval_lifecycle_and_edit_reset(rep_env):
    report_svc = rep_env["report_svc"]
    post_svc = rep_env["post_svc"]
    comment_svc = rep_env["comment_svc"]
    account_svc = rep_env["account_svc"]
    comm_id = rep_env["comm_id"]
    mod_id = rep_env["mod_id"]
    user1_id = rep_env["user1_id"]
    user2_id = rep_env["user2_id"]
    post = rep_env["post"]
    comment = rep_env["comment"]

    # Report both
    report_svc.report_post(user2_id, post.id)
    report_svc.report_comment(user2_id, comment.id)

    # Moderator approves post and comment
    report_svc.approve_item(comm_id, mod_id, "post", post.id)
    report_svc.approve_item(comm_id, mod_id, "comment", comment.id)

    # Report log should now be empty
    reports = report_svc.list_reports(comm_id, mod_id, account_svc)
    assert len(reports) == 0

    # Post is marked as approved
    refetched_post = post_svc.get_post(post.id)
    assert refetched_post.is_approved == 1

    # Reporting approved items raises AlreadyApprovedError
    with pytest.raises(AlreadyApprovedError):
        report_svc.report_post(user2_id, post.id)

    with pytest.raises(AlreadyApprovedError):
        report_svc.report_comment(user2_id, comment.id)

    # When author edits the post, is_approved resets to 0
    post_svc.update_post(post.id, user_id=user1_id, name="Edited Post Title", description="Edited post body")
    refetched_post_after_edit = post_svc.get_post(post.id)
    assert refetched_post_after_edit.is_approved == 0

    # Now it can be reported again!
    report_svc.report_post(user2_id, post.id)
    reports = report_svc.list_reports(comm_id, mod_id, account_svc)
    assert len(reports) == 1
    assert reports[0]["title"] == "Edited Post Title"

    # When author edits the comment, is_approved resets to 0
    comment_svc.update_comment(comment.id, user_id=user1_id, description="Edited comment body")
    refetched_comment = comment_svc.get_comment(comment.id)
    assert refetched_comment.is_approved == 0

    # Now comment can be reported again
    report_svc.report_comment(user2_id, comment.id)
    reports = report_svc.list_reports(comm_id, mod_id, account_svc)
    assert len(reports) == 2


def test_moderator_deletes_reported_item(rep_env):
    report_svc = rep_env["report_svc"]
    post_svc = rep_env["post_svc"]
    account_svc = rep_env["account_svc"]
    comm_id = rep_env["comm_id"]
    mod_id = rep_env["mod_id"]
    user2_id = rep_env["user2_id"]
    post = rep_env["post"]

    report_svc.report_post(user2_id, post.id)
    assert len(report_svc.list_reports(comm_id, mod_id, account_svc)) == 1

    # Delete reported post
    report_svc.delete_reported_item(comm_id, mod_id, "post", post.id)

    # Report log cleared and post deleted
    assert len(report_svc.list_reports(comm_id, mod_id, account_svc)) == 0
    with pytest.raises(PostNotFoundError):
        post_svc.get_post(post.id)
