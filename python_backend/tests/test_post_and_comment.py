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
    CommentNotFoundError,
    CommunityNotFoundError,
    UnauthorizedActionError,
)


@pytest.fixture
def setup_env(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    account_repo = SqliteAccountRepository(db)
    comm_repo = SqliteCommunityRepository(db)
    post_repo = SqlitePostRepository(db)
    comment_repo = SqliteCommentRepository(db)

    account_svc = AccountService(account_repo)
    comm_svc = CommunityService(comm_repo)
    post_svc = PostService(post_repo, community_repository=comm_repo)
    comment_svc = CommentService(comment_repo, post_repository=post_repo)

    res = account_svc.create_account("author1", "password123")
    author_id = res["account_id"]
    comm = comm_svc.create_community(author_id, "General", "General talk", "https://pic.png")

    return {
        "author_id": author_id,
        "comm_id": comm.id,
        "account_svc": account_svc,
        "post_svc": post_svc,
        "comment_svc": comment_svc,
    }


def test_create_and_manage_post(setup_env):
    author_id = setup_env["author_id"]
    comm_id = setup_env["comm_id"]
    post_svc = setup_env["post_svc"]

    # Create post
    post = post_svc.create_post(author_id, comm_id, "Post Title", "Post Description")
    assert post.id > 0
    assert post.name == "Post Title"
    assert post.upvotes == 0 and post.downvotes == 0

    # Retrieve post
    fetched = post_svc.get_post(post.id)
    assert fetched.id == post.id

    # List posts by community
    posts = post_svc.list_posts(community_id=comm_id)
    assert len(posts) == 1

    # Non-author cannot update
    with pytest.raises(UnauthorizedActionError):
        post_svc.update_post(post.id, user_id=999999, name="Hacked", description="desc")

    # Author updates
    updated = post_svc.update_post(post.id, author_id, name="New Title", description="New Desc")
    assert updated.name == "New Title"

    # Cannot create post in non-existent community
    with pytest.raises(CommunityNotFoundError):
        post_svc.create_post(author_id, community_id=999999, name="Title", description="Desc")


def test_create_and_manage_comment(setup_env):
    author_id = setup_env["author_id"]
    comm_id = setup_env["comm_id"]
    post_svc = setup_env["post_svc"]
    comment_svc = setup_env["comment_svc"]

    post = post_svc.create_post(author_id, comm_id, "Post 1", "Desc")

    # Create comment
    comment = comment_svc.create_comment(author_id, post.id, "First comment!")
    assert comment.id > 0
    assert comment.description == "First comment!"
    assert comment.upvotes == 0 and comment.downvotes == 0

    # List comments by post
    comments = comment_svc.list_comments(post.id)
    assert len(comments) == 1
    assert comments[0].id == comment.id

    # Author updates comment
    updated = comment_svc.update_comment(comment.id, author_id, "Edited comment")
    assert updated.description == "Edited comment"

    # Non-author cannot delete
    with pytest.raises(UnauthorizedActionError):
        comment_svc.delete_comment(comment.id, user_id=999999)

    # Author deletes comment
    comment_svc.delete_comment(comment.id, author_id)
    with pytest.raises(CommentNotFoundError):
        comment_svc.get_comment(comment.id)
