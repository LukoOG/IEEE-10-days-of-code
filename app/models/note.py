from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    content: Mapped[str]

    owner_id: Mapped[str] = mapped_column(ForeignKey="users.id")

    owner = relationship(
        "User",
        back_populates="notes"
    )