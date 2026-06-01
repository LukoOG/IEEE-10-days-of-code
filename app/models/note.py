from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    content: Mapped[str]

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"))

    owner = relationship("User", back_populates="notes")

    ai_summary: Mapped[str | None] = mapped_column(nullable=True)

    ai_tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
