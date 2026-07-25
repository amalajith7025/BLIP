from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    artifact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    investigation_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("investigations.investigation_id"),
        nullable=False,
    )

    artifact_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    artifact_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    investigation: Mapped["Investigation"] = relationship(
        "Investigation",
        back_populates="artifacts",
    )

    facts: Mapped[list["Fact"]] = relationship(
        "Fact",
        back_populates="artifact",
    )