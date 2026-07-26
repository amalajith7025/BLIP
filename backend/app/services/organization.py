from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud import organization as organization_crud
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationStatus,
    OrganizationUpdate,
)


class OrganizationService:

    @staticmethod
    def create_organization(
        db: Session,
        organization: OrganizationCreate,
    ) -> Organization:
        if organization_crud.get_by_name(db, organization.name):
            raise ValueError("Organization name already exists")

        try:
            return organization_crud.create(db, organization)
        except IntegrityError as error:
            db.rollback()
            raise ValueError("Organization name already exists") from error

    @staticmethod
    def get_organization(
        db: Session,
        organization_id: UUID,
    ) -> Organization | None:
        return organization_crud.get_by_id(db, organization_id)

    @staticmethod
    def list_organizations(
        db: Session,
        current_user: User | None = None,
    ) -> list[Organization]:
        organizations = organization_crud.get_all(db)
        if current_user is None:
            return organizations

        return [
            organization
            for organization in organizations
            if organization.organization_id == current_user.organization_id
        ]

    @staticmethod
    def update_organization(
        db: Session,
        organization_id: UUID,
        organization: OrganizationUpdate,
    ) -> Organization | None:
        existing = (
            organization_crud.get_by_name(db, organization.name)
            if organization.name is not None
            else None
        )
        if existing is not None and existing.organization_id != organization_id:
            raise ValueError("Organization name already exists")

        try:
            return organization_crud.update(db, organization_id, organization)
        except IntegrityError as error:
            db.rollback()
            raise ValueError("Organization name already exists") from error

    @staticmethod
    def update_organization_status(
        db: Session,
        organization_id: UUID,
        status: OrganizationStatus,
    ) -> Organization | None:
        return organization_crud.update_status(
            db,
            organization_id,
            status.value,
        )
