from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Investigation(Base):
    __tablename__ = "investigations"

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.organization_id"),
        nullable=False,
    )

    organization_unit_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organization_units.organization_unit_id"),
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="investigations",
    )

    organization_unit: Mapped["OrganizationUnit"] = relationship(
        "OrganizationUnit",
        back_populates="investigations",
    )

    business_questions: Mapped[list["BusinessQuestion"]] = relationship(
        "BusinessQuestion",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    artifacts: Mapped[list["Artifact"]] = relationship(
        "Artifact",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    facts: Mapped[list["Fact"]] = relationship(
        "Fact",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    hypotheses: Mapped[list["Hypothesis"]] = relationship(
        "Hypothesis",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    findings: Mapped[list["Finding"]] = relationship(
        "Finding",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )

    recommendations: Mapped[list["Recommendation"]] = relationship(
        "Recommendation",
        back_populates="investigation",
        cascade="all, delete-orphan",
    )