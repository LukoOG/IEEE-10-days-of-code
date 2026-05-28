from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )
    
    password_hash: Mapped[str]
    
    notes = relationship(
        "Note",
        back_populates="owner"
    )