"""Físico: actividades que definís vos (con sus campos y sesiones), asistencia, peso y nutrición.

Es lo único que importan los otros módulos.
"""

from fastapi import APIRouter

from app.modules.fisico.controllers import (
    actividades_controller,
    asistencia_controller,
    nutricion_controller,
    peso_controller,
    sesiones_controller,
)
from app.modules.fisico.models.actividades_model import Activity
from app.modules.fisico.models.peso_model import WeightLog
from app.modules.fisico.services.actividades_service import list_activities
from app.modules.fisico.services.asistencia_service import attended_days

router = APIRouter(tags=["fisico"])
for controller in (
    actividades_controller,
    asistencia_controller,
    sesiones_controller,
    peso_controller,
    nutricion_controller,
):
    router.include_router(controller.router)

__all__ = ["Activity", "WeightLog", "attended_days", "list_activities", "router"]
