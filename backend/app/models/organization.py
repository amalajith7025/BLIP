from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("tenants.tenant_id"),
        nullable=False,
    )

    organization_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="organizations",
    )

    investigations: Mapped[list["Investigation"]] = relationship(
        "Investigation",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    organization_industries: Mapped[list["OrganizationIndustry"]] = relationship(
        "OrganizationIndustry",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    organization_units: Mapped[list["OrganizationUnit"]] = relationship(
        "OrganizationUnit",
        back_populates="organization",
        cascade="all, delete-orphan",
    )