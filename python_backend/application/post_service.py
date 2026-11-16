from domain.errors import (
    CommunityNotFoundError,
    PostNotFoundError,
    UnauthorizedActionError,
)
from domain.post import Post


class PostService:
    def __init__(self, repository, community_repository=None):
        self._repository = repository
        self._community_repository = community_repository

    def create_post(
        self,
        author_id: int,
        community_id: int,
        name: str,
        description: str,
    ) -> Post:
        if self._community_repository:
            community = self._community_repository.find_by_id(community_id)
            if community is None:
                raise CommunityNotFoundError()

        post = Post.create(
            author_id=author_id,
            community_id=community_id,
            name=name,
            description=description,
        )
        self._repository.add(post)
        return post

    def get_post(self, post_id: int) -> Post:
        post = self._repository.find_by_id(post_id)
        if post is None:
            raise PostNotFoundError()
        return post

    def list_posts(self, community_id: int | None = None) -> list[Post]:
        if community_id is not None:
            return self._repository.list_by_community(community_id)
        return self._repository.list_all()

    def update_post(
        self,
        post_id: int,
        user_id: int,
        name: str,
        description: str,
    ) -> Post:
        existing = self.get_post(post_id)
        if existing.author_id != user_id:
            raise UnauthorizedActionError("Only the post author can edit this post")
        updated = Post(
            id=existing.id,
            author_id=existing.author_id,
            community_id=existing.community_id,
            name=name.strip(),
            description=description.strip(),
            upvotes=existing.upvotes,
            downvotes=existing.downvotes,
        )
        self._repository.update(updated)
        return updated

    def vote(self, post_id: int, user_id: int, direction: int) -> dict:
        self.get_post(post_id)  # ensure post exists
        upvotes, downvotes, user_vote = self._repository.vote(user_id, post_id, direction)
        return {
            "post_id": post_id,
            "upvotes": upvotes,
            "downvotes": downvotes,
            "user_vote": user_vote,
        }

    def get_user_vote(self, post_id: int, user_id: int) -> int:
        return self._repository.get_user_vote(user_id, post_id)

    def delete_post(self, post_id: int, user_id: int) -> None:
        existing = self.get_post(post_id)
        if existing.author_id != user_id:
            raise UnauthorizedActionError("Only the post author can delete this post")
        self._repository.delete(post_id)
