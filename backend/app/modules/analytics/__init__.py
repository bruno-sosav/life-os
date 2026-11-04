"""Analytics: pantalla Stats (cumplimiento, KPIs, radar y series). No tiene tablas propias."""

from fastapi import APIRouter

from app.modules.analytics.controllers import calendario_controller, resumen_controller

router = APIRouter(prefix="/analytics", tags=["analytics"])
router.include_router(resumen_controller.router)
router.include_router(calendario_controller.router)

__all__ = ["router"]
