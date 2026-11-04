from datetime import date

from sqlalchemy import CheckConstraint, Date, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, STATUS, Base, CreatedAt, UUIDPk


class Book(UUIDPk, CreatedAt, Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="rating"),)

    title: Mapped[str] = mapped_column(String(NAME))
    author: Mapped[str | None] = mapped_column(String(NAME))
    status: Mapped[str] = mapped_column(String(STATUS), default="pendiente")
    rating: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[date | None] = mapped_column(Date)
    finished_at: Mapped[date | None] = mapped_column(Date)
