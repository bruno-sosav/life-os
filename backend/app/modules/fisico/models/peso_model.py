from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Date,
    Numeric,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import Base, CreatedAt, UUIDPk


class WeightLog(UUIDPk, CreatedAt, Base):
    __tablename__ = "weight_logs"

    date: Mapped[date] = mapped_column(Date, unique=True)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)


class WeightGoal(UUIDPk, CreatedAt, Base):
    """Una sola fila: la meta de peso que se marca en el gráfico."""

    __tablename__ = "weight_goals"

    weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
