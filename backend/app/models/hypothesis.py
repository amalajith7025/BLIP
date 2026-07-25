from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Hypothesis(Base):
    __tablename__ = "hypotheses"

    hypothesis_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("investigations.investigation_id"),
        nullable=False,
    )

    hypothesis_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    investigation: Mapped["Investigation"] = relationship(
        "Investigation",
        back_populates="hypotheses",
    )

    evidence_links: Mapped[list["HypothesisEvidence"]] = relationship(
        "HypothesisEvidence",
        back_populates="hypothesis",
    )