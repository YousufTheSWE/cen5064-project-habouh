import pytest

from application.account_service import AccountService
from application.community_service import CommunityService
from data.account_repository import SqliteAccountRepository
from data.community_repository import SqliteCommunityRepository
from data.database import Database
from domain.community import Community
from domain.errors import (
    CommunityLimitExceededError,
    CommunityNotFoundError,
    UnauthorizedActionError,
    UserNotFoundError,
)


@pytest.fixture
def app_services(tmp_path):
    db = Database(str(tmp_path / "test.db"))
    account_repo = SqliteAccountRepository(db)
    comm_repo = SqliteCommunityRepository(db)
    account_svc = AccountService(account_repo)
    comm_svc = CommunityService(comm_repo)
    return account_svc, comm_svc


def test_create_and_list_communities(app_services):
    account_svc, comm_svc = app_services
    res = account_svc.create_account("owner1", "password123")
    owner_id = res["account_id"]

    comm = comm_svc.create_community(
        owner_id=owner_id,
        name="Tech",
        description="All tech discussions",
        picture="https://example.com/tech.png",
    )
    assert comm.id > 0
    assert comm.name == "Tech"
    assert comm.owner_id == owner_id

    communities = comm_svc.list_communities()
    assert len(communities) == 1
    assert communities[0].id == comm.id


def test_community_ownership_limit_max_10(app_services):
    account_svc, comm_svc = app_services
    res = account_svc.create_account("bigowner", "password123")
    owner_id = res["account_id"]

    # Create 10 communities
    for i in range(10):
        comm_svc.create_community(
            owner_id=owner_id,
            name=f"Community {i}",
            description="test",
            picture="https://example.com/pic.png",
        )

    # 11th community creation must fail
    with pytest.raises(CommunityLimitExceededError):
        comm_svc.create_community(
            owner_id=owner_id,
            name="Community 11",
            description="overflow",
            picture="https://example.com/pic.png",
        )


def test_transfer_ownership_by_username_and_id(app_services):
    account_svc, comm_svc = app_services
    res1 = account_svc.create_account("alice_owner", "password123")
    res2 = account_svc.create_account("bob_recipient", "password123")
    alice_id = res1["account_id"]
    bob_id = res2["account_id"]

    comm = comm_svc.create_community(alice_id, "AliceComm", "desc", "https://pic.png")

    # Transfer by username
    transferred = comm_svc.transfer_ownership(comm.id, alice_id, "bob_recipient", account_svc)
    assert transferred.owner_id == bob_id

    # Now bob is owner; transfer back to alice by user ID string
    transferred_back = comm_svc.transfer_ownership(comm.id, bob_id, str(alice_id), account_svc)
    assert transferred_back.owner_id == alice_id


def test_transfer_ownership_validations(app_services):
    account_svc, comm_svc = app_services
    res1 = account_svc.create_account("owner", "password123")
    res2 = account_svc.create_account("stranger", "password123")
    owner_id = res1["account_id"]
    stranger_id = res2["account_id"]

    comm = comm_svc.create_community(owner_id, "Comm", "desc", "https://pic.png")

    # Non-owner cannot transfer
    with pytest.raises(UnauthorizedActionError):
        comm_svc.transfer_ownership(comm.id, stranger_id, "stranger", account_svc)

    # Cannot transfer to non-existent user
    with pytest.raises(UserNotFoundError):
        comm_svc.transfer_ownership(comm.id, owner_id, "ghost_user", account_svc)

    # Cannot transfer if recipient already owns 10 communities
    for i in range(10):
        comm_svc.create_community(stranger_id, f"StrangerComm {i}", "desc", "https://pic.png")

    with pytest.raises(CommunityLimitExceededError):
        comm_svc.transfer_ownership(comm.id, owner_id, "stranger", account_svc)


def test_update_and_delete_community(app_services):
    account_svc, comm_svc = app_services
    res1 = account_svc.create_account("commowner", "password123")
    res2 = account_svc.create_account("otherperson", "password123")
    owner_id = res1["account_id"]
    other_id = res2["account_id"]

    comm = comm_svc.create_community(owner_id, "Original", "desc", "https://pic.png")

    # Other user cannot update
    with pytest.raises(UnauthorizedActionError):
        comm_svc.update_community(comm.id, other_id, "Hacked", "desc", "https://pic.png")

    # Owner updates
    updated = comm_svc.update_community(comm.id, owner_id, "Updated Name", "new desc", "https://new.png")
    assert updated.name == "Updated Name"

    # Other user cannot delete
    with pytest.raises(UnauthorizedActionError):
        comm_svc.delete_community(comm.id, other_id)

    # Owner deletes
    comm_svc.delete_community(comm.id, owner_id)
    with pytest.raises(CommunityNotFoundError):
        comm_svc.get_community(comm.id)


def test_domain_community_limit_validation():
    # Below limit should pass without error
    Community.validate_owner_community_count(0)
    Community.validate_owner_community_count(9)

    # At or above limit should raise CommunityLimitExceededError
    with pytest.raises(CommunityLimitExceededError):
        Community.validate_owner_community_count(10)

    with pytest.raises(CommunityLimitExceededError):
        Community.validate_owner_community_count(15)

