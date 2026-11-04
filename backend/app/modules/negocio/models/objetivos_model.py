from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, Base, CreatedAt, UUIDPk


class StratusGoal(UUIDPk, CreatedAt, Base):
    __tablename__ = "stratus_goals"
    __table_args__ = (CheckConstraint("progress BETWEEN 0 AND 100", name="progress"),)

    month: Mapped[date] = mapped_column(Date, index=True)  # primer día del mes
    title: Mapped[str] = mapped_column(String(NAME))
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
