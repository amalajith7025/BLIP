from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    recommendation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("investigations.investigation_id"),
        nullable=False,
    )

    finding_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("findings.finding_id"),
        nullable=False,
    )

    recommendation_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    investigation: Mapped["Investigation"] = relationship(
        "Investigation",
        back_populates="recommendations",
    )

    finding: Mapped["Finding"] = relationship(
        "Finding",
        back_populates="recommendations",
    )