from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.finanzas import finanzas_service as service
from app.modules.finanzas.finanzas_model import FinanceExpense, FinanceIncome
from app.modules.finanzas.finanzas_schema import ExpenseIn, ExpenseOut, IncomeIn, IncomeOut

router = APIRouter(prefix="/finance", tags=["finanzas"])


@router.get("/income", response_model=list[IncomeOut])
def list_income(month: date, session: SessionDep) -> list[FinanceIncome]:
    return service.list_income(session, month)


@router.post("/income", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeIn, session: SessionDep) -> FinanceIncome:
    return service.create_income(session, payload)


@router.delete("/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: str, session: SessionDep) -> Response:
    service.delete_income(session, income_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(month: date, session: SessionDep) -> list[FinanceExpense]:
    return service.list_expenses(session, month)


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseIn, session: SessionDep) -> FinanceExpense:
    return service.create_expense(session, payload)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str, session: SessionDep) -> Response:
    service.delete_expense(session, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
