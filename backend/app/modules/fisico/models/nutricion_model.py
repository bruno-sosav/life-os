from datetime import date
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    Integer,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class NutritionLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "nutrition_logs"
    __table_args__ = (CheckConstraint("quality_score BETWEEN 1 AND 5", name="quality_score"),)

    date: Mapped[date] = mapped_column(Date, unique=True)
    quality_score: Mapped[int | None] = mapped_column(Integer)
    meals_count: Mapped[int | None] = mapped_column(Integer)
    water_liters: Mapped[Decimal | None] = mapped_column(Numeric(4, 2))
    notes: Mapped[str | None] = mapped_column(Text)
