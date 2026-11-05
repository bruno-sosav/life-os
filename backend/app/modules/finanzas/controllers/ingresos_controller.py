from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.finanzas.models.ingresos_model import FinanceIncome
from app.modules.finanzas.schemas.ingresos_schema import IncomeIn, IncomeOut
from app.modules.finanzas.services import ingresos_service

router = APIRouter()


@router.get("/income", response_model=list[IncomeOut])
def list_income(month: date, session: SessionDep) -> list[FinanceIncome]:
    return ingresos_service.list_income(session, month)


@router.post("/income", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeIn, session: SessionDep) -> FinanceIncome:
    return ingresos_service.create_income(session, payload)


@router.delete("/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: str, session: SessionDep) -> Response:
    ingresos_service.delete_income(session, income_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
