from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class OrganizationIndustry(Base):
    __tablename__ = "organization_industries"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "industry_id",
            name="uq_organization_industry",
        ),
    )

    organization_industry_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    organization_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.organization_id"),
        nullable=False,
    )

    industry_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("industries.industry_id"),
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="organization_industries",
    )

    industry: Mapped["Industry"] = relationship(
        "Industry",
        back_populates="organization_industries",
    )