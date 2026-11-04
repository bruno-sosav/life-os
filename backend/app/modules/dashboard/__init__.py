"""Dashboard (pantalla Hoy): racha, agenda del día y cierre semanal. No tiene tablas propias:
lee lo de Rutina, Físico y Mental a través de sus fachadas."""

from fastapi import APIRouter

from app.modules.dashboard.controllers import agenda_controller, cierre_controller, racha_controller

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
for controller in (racha_controller, agenda_controller, cierre_controller):
    router.include_router(controller.router)

__all__ = ["router"]
