from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Fact(Base):
    __tablename__ = "facts"

    fact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("investigations.investigation_id"),
        nullable=False,
    )

    artifact_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("artifacts.artifact_id"),
        nullable=True,
    )

    fact_statement: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    investigation: Mapped["Investigation"] = relationship(
        "Investigation",
        back_populates="facts",
    )

    artifact: Mapped["Artifact"] = relationship(
        "Artifact",
        back_populates="facts",
    )

    evidence: Mapped[list["Evidence"]] = relationship(
        "Evidence",
        back_populates="fact",
    )