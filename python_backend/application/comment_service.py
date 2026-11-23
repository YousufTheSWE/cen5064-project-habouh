from domain.comment import Comment
from domain.errors import (
    CommentNotFoundError,
    PostNotFoundError,
    UnauthorizedActionError,
    UserBannedError,
)


class CommentService:
    def __init__(self, repository, post_repository=None, community_repository=None):
        self._repository = repository
        self._post_repository = post_repository
        self._community_repository = community_repository

    def create_comment(
        self,
        author_id: int,
        post_id: int,
        description: str,
    ) -> Comment:
        if self._post_repository:
            post = self._post_repository.find_by_id(post_id)
            if post is None:
                raise PostNotFoundError()
            if self._community_repository and self._community_repository.is_banned(post.community_id, author_id):
                raise UserBannedError("You are banned from commenting in this community")

        comment = Comment.create(
            author_id=author_id,
            post_id=post_id,
            description=description,
        )
        self._repository.add(comment)
        return comment

    def get_comment(self, comment_id: int) -> Comment:
        comment = self._repository.find_by_id(comment_id)
        if comment is None:
            raise CommentNotFoundError()
        return comment

    def list_comments(self, post_id: int) -> list[Comment]:
        return self._repository.list_by_post(post_id)

    def update_comment(
        self,
        comment_id: int,
        user_id: int,
        description: str,
    ) -> Comment:
        existing = self.get_comment(comment_id)
        if existing.author_id != user_id:
            raise UnauthorizedActionError("Only the comment author can edit this comment")
        updated = Comment(
            id=existing.id,
            author_id=existing.author_id,
            post_id=existing.post_id,
            description=description.strip(),
            upvotes=existing.upvotes,
            downvotes=existing.downvotes,
            is_approved=0,  # resets approval on edit
        )
        self._repository.update(updated)
        return updated

    def vote(self, comment_id: int, user_id: int, direction: int) -> dict:
        self.get_comment(comment_id)  # ensure comment exists
        upvotes, downvotes, user_vote = self._repository.vote(user_id, comment_id, direction)
        return {
            "comment_id": comment_id,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "user_vote": user_vote,
        }

    def get_user_vote(self, comment_id: int, user_id: int) -> int:
        return self._repository.get_user_vote(user_id, comment_id)

    def delete_comment(self, comment_id: int, user_id: int) -> None:
        existing = self.get_comment(comment_id)
        is_mod_or_owner = False
        if self._post_repository and self._community_repository:
            post = self._post_repository.find_by_id(existing.post_id)
            if post:
                comm = self._community_repository.find_by_id(post.community_id)
                if comm and comm.owner_id == user_id or self._community_repository.is_moderator(post.community_id, user_id):
                    is_mod_or_owner = True

        if existing.author_id != user_id and not is_mod_or_owner:
            raise UnauthorizedActionError("Only the comment author or a moderator can delete this comment")
        self._repository.delete(comment_id)
