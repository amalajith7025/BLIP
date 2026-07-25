from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HypothesisEvidence(Base):
    __tablename__ = "hypothesis_evidence"

    hypothesis_evidence_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    hypothesis_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hypotheses.hypothesis_id"),
        nullable=False,
    )

    evidence_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("evidence.evidence_id"),
        nullable=False,
    )

    hypothesis: Mapped["Hypothesis"] = relationship(
        "Hypothesis",
        back_populates="evidence_links",
    )

    evidence: Mapped["Evidence"] = relationship(
        "Evidence",
        back_populates="hypothesis_links",
    )