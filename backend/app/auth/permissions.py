from __future__ import annotations

from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.authorization import (
    AuthorizationError,
    require_authenticated_user,
    require_investigation_access,
    require_organization_member,
    require_role,
    require_workspace_member,
    require_workspace_owner,
)
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.crud.membership import get_active_for_user
from app.crud.organization import get_by_id as get_organization_by_id
from app.crud.role import get_role_by_id
from app.crud.workspace import get_by_id as get_workspace_by_id
from app.models.organization import Organization
from app.models.user import User
from app.models.workspace import Workspace


def require_authenticated_user_dependency(
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        return require_authenticated_user(current_user)
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error


def require_workspace_member_dependency(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        workspace = get_workspace_by_id(db, workspace_id)
        if workspace is None:
            raise AuthorizationError("Workspace not found")

        membership = get_active_for_user(db, workspace_id, current_user.user_id)
        require_workspace_member(current_user, workspace, membership)
        return current_user
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


def require_workspace_owner_dependency(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        workspace = get_workspace_by_id(db, workspace_id)
        if workspace is None:
            raise AuthorizationError("Workspace not found")

        membership = get_active_for_user(db, workspace_id, current_user.user_id)
        require_workspace_owner(current_user, workspace, membership)
        return current_user
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


def require_organization_member_dependency(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        organization = get_organization_by_id(db, organization_id)
        if organization is None:
            raise AuthorizationError("Organization not found")

        require_organization_member(current_user, organization)
        return current_user
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


def require_investigation_access_dependency(
    investigation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    try:
        return authorize_investigation_access(db, current_user, investigation_id)
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


def require_role_dependency(
    role_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    try:
        require_role(current_user, role_name)
        return current_user
    except AuthorizationError as error:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(error)) from error


def authorize_workspace_access(
    db: Session,
    current_user: User,
    workspace_id: UUID,
) -> Workspace:
    workspace = get_workspace_by_id(db, workspace_id)
    if workspace is None:
        raise AuthorizationError("Workspace not found")

    membership = get_active_for_user(db, workspace_id, current_user.user_id)
    require_workspace_member(current_user, workspace, membership)
    return workspace


def authorize_organization_access(
    db: Session,
    current_user: User,
    organization_id: UUID,
) -> Organization:
    organization = get_organization_by_id(db, organization_id)
    if organization is None:
        raise AuthorizationError("Organization not found")

    require_organization_member(current_user, organization)
    return organization


def authorize_investigation_access(
    db: Session,
    current_user: User,
    investigation_id: UUID,
) -> User:
    from app.crud.investigation import get_by_id as get_investigation_by_id

    investigation = get_investigation_by_id(db, investigation_id)
    if investigation is None:
        raise AuthorizationError("Investigation not found")

    organization = investigation.organization
    if organization is None:
        organization = get_organization_by_id(db, investigation.organization_id)

    require_investigation_access(current_user, organization)
    return current_user
