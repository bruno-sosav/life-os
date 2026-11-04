from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class MoodLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "mood_logs"
    __table_args__ = (
        CheckConstraint("mood_score BETWEEN 1 AND 5", name="mood_score"),
        CheckConstraint("energy_score BETWEEN 1 AND 5", name="energy_score"),
    )

    date: Mapped[date] = mapped_column(Date, unique=True)
    mood_score: Mapped[int | None] = mapped_column(Integer)
    sleep_hours: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    energy_score: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
