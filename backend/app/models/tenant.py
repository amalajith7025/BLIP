from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    tenant_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    tenant_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    subscription_plan: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="FREE",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE",
    )

    organizations: Mapped[list["Organization"]] = relationship(
        "Organization",
        back_populates="tenant",
        cascade="all, delete-orphan",
    )