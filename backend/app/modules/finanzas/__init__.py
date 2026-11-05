"""Finanzas: ingresos por mes, gastos por día y el resumen del mes. Es lo único que ven los otros
módulos."""

from fastapi import APIRouter

from app.modules.finanzas.controllers import (
    gastos_controller,
    ingresos_controller,
    resumen_controller,
)
from app.modules.finanzas.models.gastos_model import FinanceExpense
from app.modules.finanzas.models.ingresos_model import FinanceIncome

router = APIRouter(prefix="/finance", tags=["finanzas"])
for controller in (resumen_controller, ingresos_controller, gastos_controller):
    router.include_router(controller.router)

__all__ = ["FinanceExpense", "FinanceIncome", "router"]
