from domain.errors import (
    AlreadyApprovedError,
    CommentNotFoundError,
    PostNotFoundError,
    UnauthorizedActionError,
    UserBannedError,
)


class ReportService:
    def __init__(
        self,
        report_repository,
        post_repository,
        comment_repository,
        community_repository,
    ):
        self._report_repo = report_repository
        self._post_repo = post_repository
        self._comment_repo = comment_repository
        self._comm_repo = community_repository

    def _check_moderator_or_owner(self, community_id: int, user_id: int) -> None:
        comm = self._comm_repo.find_by_id(community_id)
        is_owner = comm and comm.owner_id == user_id
        is_mod = self._comm_repo.is_moderator(community_id, user_id)
        if not (is_owner or is_mod):
            raise UnauthorizedActionError("Only community moderators or the owner can perform this action")

    def report_post(self, user_id: int, post_id: int) -> None:
        post = self._post_repo.find_by_id(post_id)
        if post is None:
            raise PostNotFoundError()

        if self._comm_repo.is_banned(post.community_id, user_id):
            raise UserBannedError("Banned users cannot report posts in this community")

        if post.is_approved:
            raise AlreadyApprovedError("This post has already been approved and cannot be reported unless edited")

        self._report_repo.add_report(post.community_id, "post", post_id, user_id)

    def report_comment(self, user_id: int, comment_id: int) -> None:
        comment = self._comment_repo.find_by_id(comment_id)
        if comment is None:
            raise CommentNotFoundError()

        post = self._post_repo.find_by_id(comment.post_id)
        if post is None:
            raise PostNotFoundError()

        if self._comm_repo.is_banned(post.community_id, user_id):
            raise UserBannedError("Banned users cannot report comments in this community")

        if comment.is_approved:
            raise AlreadyApprovedError("This comment has already been approved and cannot be reported unless edited")

        self._report_repo.add_report(post.community_id, "comment", comment_id, user_id)

    def list_reports(self, community_id: int, user_id: int, account_service) -> list[dict]:
        self._check_moderator_or_owner(community_id, user_id)
        grouped_reports = self._report_repo.list_reports_by_community(community_id)
        result = []

        for item in grouped_reports:
            target_type = item["target_type"]
            target_id = item["target_id"]
            reporter_ids = item["reporter_ids"]
            reporters = [
                {"id": r_id, "username": account_service.get_username_by_id(r_id)}
                for r_id in reporter_ids
            ]

            if target_type == "post":
                post = self._post_repo.find_by_id(target_id)
                if post is None:
                    self._report_repo.delete_reports_for_target("post", target_id)
                    continue
                result.append({
                    "target_type": "post",
                    "target_id": post.id,
                    "community_id": post.community_id,
                    "title": post.name,
                    "content": post.description,
                    "author_id": post.author_id,
                    "author_username": account_service.get_username_by_id(post.author_id),
                    "is_approved": post.is_approved,
                    "reporters": reporters,
                    "report_count": len(reporters),
                    "latest_report_time": item["latest_report_time"],
                })
            elif target_type == "comment":
                comment = self._comment_repo.find_by_id(target_id)
                if comment is None:
                    self._report_repo.delete_reports_for_target("comment", target_id)
                    continue
                result.append({
                    "target_type": "comment",
                    "target_id": comment.id,
                    "post_id": comment.post_id,
                    "community_id": community_id,
                    "title": f"Comment on Post #{comment.post_id}",
                    "content": comment.description,
                    "author_id": comment.author_id,
                    "author_username": account_service.get_username_by_id(comment.author_id),
                    "is_approved": comment.is_approved,
                    "reporters": reporters,
                    "report_count": len(reporters),
                    "latest_report_time": item["latest_report_time"],
                })

        return result

    def approve_item(self, community_id: int, user_id: int, target_type: str, target_id: int) -> None:
        self._check_moderator_or_owner(community_id, user_id)
        if target_type == "post":
            self._post_repo.set_approved(target_id, 1)
        elif target_type == "comment":
            self._comment_repo.set_approved(target_id, 1)
        self._report_repo.delete_reports_for_target(target_type, target_id)

    def delete_reported_item(self, community_id: int, user_id: int, target_type: str, target_id: int) -> None:
        self._check_moderator_or_owner(community_id, user_id)
        if target_type == "post":
            self._post_repo.delete(target_id)
        elif target_type == "comment":
            self._comment_repo.delete(target_id)
        self._report_repo.delete_reports_for_target(target_type, target_id)
