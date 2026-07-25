from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrganizationUnit(Base):
    __tablename__ = "organization_units"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "unit_name",
            name="uq_organization_unit",
        ),
    )

    organization_unit_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.organization_id"),
        nullable=False,
    )

    unit_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    unit_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="organization_units",
    )

    investigations: Mapped[list["Investigation"]] = relationship(
        "Investigation",
        back_populates="organization_unit",
        cascade="all, delete-orphan",
    )