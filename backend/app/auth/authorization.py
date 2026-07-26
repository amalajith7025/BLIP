from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace


class AuthorizationError(Exception):
    pass


def require_authenticated_user(user: User | None) -> User:
    if user is None:
        raise AuthorizationError("Authentication required")
    return user


def require_workspace_member(
    user: User | None,
    workspace: Workspace | None,
    membership: Membership | None,
) -> Membership:
    require_authenticated_user(user)
    if workspace is None:
        raise AuthorizationError("Workspace not found")
    if membership is None or membership.status != "ACTIVE":
        raise AuthorizationError("Access denied for workspace")
    return membership


def require_workspace_owner(
    user: User | None,
    workspace: Workspace | None,
    membership: Membership | None,
) -> Membership:
    membership = require_workspace_member(user, workspace, membership)
    if membership.role != "OWNER":
        raise AuthorizationError("Workspace owner access required")
    return membership


def require_organization_member(
    user: User | None,
    organization: Organization | None,
) -> Organization:
    require_authenticated_user(user)
    if organization is None:
        raise AuthorizationError("Organization not found")
    if user.organization_id != organization.organization_id:
        raise AuthorizationError("Organization access denied")
    return organization


def require_investigation_access(
    user: User | None,
    organization: Organization | None,
) -> Organization:
    return require_organization_member(user, organization)


def require_role(user: User | None, role_name: str) -> Role:
    require_authenticated_user(user)
    if user.role_id is None:
        raise AuthorizationError(f"Requires role: {role_name}")
    role = user.role
    if role is None or role.role_name != role_name:
        raise AuthorizationError(f"Requires role: {role_name}")
    return role
