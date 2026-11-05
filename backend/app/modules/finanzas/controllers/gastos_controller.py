from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.finanzas.models.gastos_model import FinanceExpense
from app.modules.finanzas.schemas.gastos_schema import ExpenseIn, ExpenseOut
from app.modules.finanzas.services import gastos_service

router = APIRouter()


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(month: date, session: SessionDep) -> list[FinanceExpense]:
    return gastos_service.list_expenses(session, month)


@router.post("/expenses", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def create_expense(payload: ExpenseIn, session: SessionDep) -> FinanceExpense:
    return gastos_service.create_expense(session, payload)


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str, session: SessionDep) -> Response:
    gastos_service.delete_expense(session, expense_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
