from uuid import uuid4

from app.auth.authorization import (
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

user = User(
    user_id=uuid4(),
    organization_id=uuid4(),
    role_id=uuid4(),
    email='u@example.com',
    password_hash='x',
    first_name='A',
    last_name='B',
    is_active=True,
)
assert require_authenticated_user(user) is user
workspace = Workspace(workspace_id=uuid4(), owner_id=user.user_id, slug='ws')
membership = Membership(user_id=user.user_id, workspace_id=workspace.workspace_id, role='OWNER', status='ACTIVE')
assert require_workspace_member(user, workspace, membership) is membership
assert require_workspace_owner(user, workspace, membership) is membership
organization = Organization(organization_id=user.organization_id, tenant_id=uuid4(), name='Org')
assert require_organization_member(user, organization) is organization
role = Role(role_id=user.role_id, role_name='Platform Admin')
user.role = role
assert require_role(user, 'Platform Admin') is role
print('authorization helpers verified')
