from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base_model import NAME, Base, CreatedAt, UUIDPk


class FinanceIncome(UUIDPk, CreatedAt, Base):
    __tablename__ = "finance_income"

    month: Mapped[date] = mapped_column(Date, index=True)  # primer día del mes
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    source: Mapped[str | None] = mapped_column(String(NAME))  # 'sueldo' | 'freelance' | 'otro'
    notes: Mapped[str | None] = mapped_column(Text)


class FinanceExpense(UUIDPk, CreatedAt, Base):
    __tablename__ = "finance_expenses"

    date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    category: Mapped[str] = mapped_column(String(NAME))
    description: Mapped[str | None] = mapped_column(Text)
