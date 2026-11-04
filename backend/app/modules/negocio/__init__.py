"""Negocio (Stratus): tableros por proyecto, ideas y objetivos del mes."""

from fastapi import APIRouter

from app.modules.negocio.controllers import (
    ideas_controller,
    objetivos_controller,
    proyectos_controller,
    tareas_controller,
)

router = APIRouter(tags=["negocio"])
for controller in (proyectos_controller, tareas_controller, ideas_controller, objetivos_controller):
    router.include_router(controller.router)

__all__ = ["router"]
