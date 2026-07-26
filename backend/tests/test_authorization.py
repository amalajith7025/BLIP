from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.auth.authorization import (
    AuthorizationError,
    require_authenticated_user,
    require_organization_member,
    require_role,
    require_workspace_member,
    require_workspace_owner,
)
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace
from app.services.organization import OrganizationService


@pytest.fixture
def db_session():
    class DummyDB:
        def __init__(self):
            self._items = []

        def query(self, *args, **kwargs):
            return self

        def filter(self, *args, **kwargs):
            return self

        def first(self):
            return None

    return DummyDB()


def make_user(user_id=None, organization_id=None, role_id=None):
    user = User(
        user_id=user_id or uuid4(),
        organization_id=organization_id or uuid4(),
        role_id=role_id or uuid4(),
        email="user@example.com",
        password_hash="hash",
        first_name="Test",
        last_name="User",
        is_active=True,
    )
    return user


def test_require_authenticated_user_returns_user():
    user = make_user()
    assert require_authenticated_user(user) is user


def test_require_authenticated_user_rejects_none():
    with pytest.raises(AuthorizationError):
        require_authenticated_user(None)


def test_require_workspace_member_allows_active_member():
    user = make_user()
    workspace = Workspace(workspace_id=uuid4(), owner_id=user.user_id, slug="ws")
    membership = Membership(user_id=user.user_id, workspace_id=workspace.workspace_id, status="ACTIVE")
    assert require_workspace_member(user, workspace, membership) is membership


def test_require_workspace_member_rejects_non_member():
    user = make_user()
    workspace = Workspace(workspace_id=uuid4(), owner_id=user.user_id, slug="ws")
    with pytest.raises(AuthorizationError):
        require_workspace_member(user, workspace, None)


def test_require_workspace_owner_rejects_non_owner():
    user = make_user()
    workspace = Workspace(workspace_id=uuid4(), owner_id=uuid4(), slug="ws")
    membership = Membership(user_id=user.user_id, workspace_id=workspace.workspace_id, role="MEMBER", status="ACTIVE")
    with pytest.raises(AuthorizationError):
        require_workspace_owner(user, workspace, membership)


def test_require_organization_member_allows_matching_org():
    user = make_user(organization_id=uuid4())
    organization = Organization(organization_id=user.organization_id, tenant_id=uuid4(), name="Org")
    assert require_organization_member(user, organization) is organization


def test_require_organization_member_rejects_other_org():
    user = make_user(organization_id=uuid4())
    organization = Organization(organization_id=uuid4(), tenant_id=uuid4(), name="Org")
    with pytest.raises(AuthorizationError):
        require_organization_member(user, organization)


def test_require_role_allows_matching_role():
    role = Role(role_id=uuid4(), role_name="Platform Admin")
    user = make_user(role_id=role.role_id)
    user.role = role
    assert require_role(user, role.role_name) is role


def test_require_role_rejects_missing_role():
    role = Role(role_id=uuid4(), role_name="Contributor")
    user = make_user(role_id=uuid4())
    with pytest.raises(AuthorizationError):
        require_role(user, role.role_name)


def test_list_organizations_filters_by_current_user_organization():
    visible_org = Organization(
        organization_id=uuid4(),
        tenant_id=uuid4(),
        name="Visible Org",
    )
    hidden_org = Organization(
        organization_id=uuid4(),
        tenant_id=uuid4(),
        name="Hidden Org",
    )
    user = make_user(organization_id=visible_org.organization_id)

    class DummyQuery:
        def __init__(self, items):
            self.items = items

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return list(self.items)

    class DummyDB:
        def __init__(self, items):
            self.items = items

        def query(self, model):
            return DummyQuery(self.items)

    db = DummyDB([visible_org, hidden_org])

    result = OrganizationService.list_organizations(db, user)

    assert result == [visible_org]
