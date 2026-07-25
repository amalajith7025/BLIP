from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("investigations.investigation_id"),
        nullable=False,
    )

    fact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("facts.fact_id"),
        nullable=False,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    evidence_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    confidence_score: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    investigation: Mapped["Investigation"] = relationship(
        "Investigation",
        back_populates="evidence",
    )

    fact: Mapped["Fact"] = relationship(
        "Fact",
        back_populates="evidence",
    )

    hypothesis_links: Mapped[list["HypothesisEvidence"]] = relationship(
        "HypothesisEvidence",
        back_populates="evidence",
    )