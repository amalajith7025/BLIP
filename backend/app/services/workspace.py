from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import membership as membership_crud
from app.crud import workspace as workspace_crud
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceNotFoundError(Exception):
    pass


class WorkspaceAccessDeniedError(Exception):
    pass


class WorkspaceConflictError(Exception):
    pass


class WorkspaceService:

    @staticmethod
    def create_workspace(
        db: Session,
        workspace: WorkspaceCreate,
        current_user: User,
    ) -> Workspace:
        if workspace_crud.get_by_slug(db, workspace.slug):
            raise WorkspaceConflictError("Workspace slug already exists")

        try:
            db_workspace = workspace_crud.create(
                db,
                workspace,
                current_user.user_id,
            )
            membership_crud.create_owner_membership(
                db,
                db_workspace.workspace_id,
                current_user.user_id,
            )
            db.commit()
            db.refresh(db_workspace)
            return db_workspace
        except IntegrityError as error:
            db.rollback()
            raise WorkspaceConflictError(
                "Workspace slug already exists"
            ) from error

    @staticmethod
    def get_workspace(
        db: Session,
        workspace_id: UUID,
        current_user: User,
    ) -> Workspace:
        workspace = workspace_crud.get_by_id(db, workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError()

        membership = membership_crud.get_active_for_user(
            db,
            workspace_id,
            current_user.user_id,
        )
        if membership is None:
            raise WorkspaceNotFoundError()

        return workspace

    @staticmethod
    def list_workspaces(
        db: Session,
        current_user: User,
    ) -> list[Workspace]:
        return workspace_crud.list_for_user(db, current_user.user_id)

    @staticmethod
    def update_workspace(
        db: Session,
        workspace_id: UUID,
        workspace_data: WorkspaceUpdate,
        current_user: User,
    ) -> Workspace:
        workspace = WorkspaceService._get_owned_workspace(
            db,
            workspace_id,
            current_user,
        )

        if workspace_data.slug is not None:
            existing = workspace_crud.get_by_slug(db, workspace_data.slug)
            if existing is not None and existing.workspace_id != workspace_id:
                raise WorkspaceConflictError("Workspace slug already exists")

        try:
            workspace_crud.update(db, workspace, workspace_data)
            db.commit()
            db.refresh(workspace)
            return workspace
        except IntegrityError as error:
            db.rollback()
            raise WorkspaceConflictError(
                "Workspace slug already exists"
            ) from error

    @staticmethod
    def delete_workspace(
        db: Session,
        workspace_id: UUID,
        current_user: User,
    ) -> None:
        workspace = WorkspaceService._get_owned_workspace(
            db,
            workspace_id,
            current_user,
        )
        workspace_crud.delete(db, workspace)
        db.commit()

    @staticmethod
    def _get_owned_workspace(
        db: Session,
        workspace_id: UUID,
        current_user: User,
    ) -> Workspace:
        workspace = workspace_crud.get_by_id(db, workspace_id)
        if workspace is None:
            raise WorkspaceNotFoundError()

        membership = membership_crud.get_active_for_user(
            db,
            workspace_id,
            current_user.user_id,
        )
        if membership is None or membership.role != "OWNER":
            raise WorkspaceAccessDeniedError()

        return workspace
