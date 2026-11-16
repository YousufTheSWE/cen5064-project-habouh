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


@pytest.fixture
def voting_env(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    account_repo = SqliteAccountRepository(db)
    comm_repo = SqliteCommunityRepository(db)
    post_repo = SqlitePostRepository(db)
    comment_repo = SqliteCommentRepository(db)

    account_svc = AccountService(account_repo)
    comm_svc = CommunityService(comm_repo)
    post_svc = PostService(post_repo, community_repository=comm_repo)
    comment_svc = CommentService(comment_repo, post_repository=post_repo)

    res1 = account_svc.create_account("voter1", "password123")
    res2 = account_svc.create_account("voter2", "password123")
    u1 = res1["account_id"]
    u2 = res2["account_id"]

    comm = comm_svc.create_community(u1, "VoteComm", "desc", "https://pic.png")
    post = post_svc.create_post(u1, comm.id, "Vote Post", "Post body")
    comment = comment_svc.create_comment(u1, post.id, "Vote comment body")

    return {
        "u1": u1,
        "u2": u2,
        "post_id": post.id,
        "comment_id": comment.id,
        "post_svc": post_svc,
        "comment_svc": comment_svc,
    }


def test_post_voting_lifecycle(voting_env):
    post_svc = voting_env["post_svc"]
    post_id = voting_env["post_id"]
    u1 = voting_env["u1"]
    u2 = voting_env["u2"]

    # Initial state: 0 upvotes, 0 downvotes, user vote 0
    p = post_svc.get_post(post_id)
    assert p.upvotes == 0 and p.downvotes == 0
    assert post_svc.get_user_vote(post_id, u1) == 0

    # u1 Upvotes (+1)
    res = post_svc.vote(post_id, u1, 1)
    assert res["upvotes"] == 1 and res["downvotes"] == 0 and res["user_vote"] == 1

    # u1 Upvotes again with 0 (cancels vote)
    res = post_svc.vote(post_id, u1, 0)
    assert res["upvotes"] == 0 and res["downvotes"] == 0 and res["user_vote"] == 0

    # u1 Downvotes (-1)
    res = post_svc.vote(post_id, u1, -1)
    assert res["upvotes"] == 0 and res["downvotes"] == 1 and res["user_vote"] == -1

    # u1 switches directly to Upvote (+1)
    res = post_svc.vote(post_id, u1, 1)
    assert res["upvotes"] == 1 and res["downvotes"] == 0 and res["user_vote"] == 1

    # u2 also Upvotes (+1)
    res2 = post_svc.vote(post_id, u2, 1)
    assert res2["upvotes"] == 2 and res2["downvotes"] == 0 and res2["user_vote"] == 1

    # Verify cached counters in post entity
    p_final = post_svc.get_post(post_id)
    assert p_final.upvotes == 2 and p_final.downvotes == 0


def test_comment_voting_lifecycle(voting_env):
    comment_svc = voting_env["comment_svc"]
    comment_id = voting_env["comment_id"]
    u1 = voting_env["u1"]
    u2 = voting_env["u2"]

    # u1 Upvotes comment
    res = comment_svc.vote(comment_id, u1, 1)
    assert res["upvotes"] == 1 and res["downvotes"] == 0 and res["user_vote"] == 1

    # u2 Downvotes comment
    res2 = comment_svc.vote(comment_id, u2, -1)
    assert res2["upvotes"] == 1 and res2["downvotes"] == 1 and res2["user_vote"] == -1

    # u1 cancels vote (0)
    res = comment_svc.vote(comment_id, u1, 0)
    assert res["upvotes"] == 0 and res["downvotes"] == 1 and res["user_vote"] == 0

    # Verify comment entity
    c_final = comment_svc.get_comment(comment_id)
    assert c_final.upvotes == 0 and c_final.downvotes == 1
