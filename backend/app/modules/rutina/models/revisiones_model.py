from datetime import date

from sqlalchemy import Date, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class WeeklyReview(UUIDPk, CreatedAt, Base):
    __tablename__ = "weekly_reviews"

    week_start: Mapped[date] = mapped_column(Date, unique=True)  # lunes de esa semana
    went_well: Mapped[str | None] = mapped_column(Text)
    would_change: Mapped[str | None] = mapped_column(Text)
