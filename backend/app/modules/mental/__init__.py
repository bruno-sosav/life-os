"""Mental: skills que practicás, listas libres y el mood del día.

Es lo único que ven los otros módulos.
"""

from fastapi import APIRouter

from app.modules.mental.controllers import (
    listas_controller,
    mood_controller,
    practicas_controller,
    recursos_controller,
    skills_controller,
)
from app.modules.mental.models.mood_model import MoodLog
from app.modules.mental.models.practicas_model import Practice
from app.modules.mental.models.skills_model import Skill
from app.modules.mental.services.mood_service import avg_mood

router = APIRouter(tags=["mental"])
for controller in (
    skills_controller,
    practicas_controller,
    recursos_controller,
    listas_controller,
    mood_controller,
):
    router.include_router(controller.router)

__all__ = ["MoodLog", "Practice", "Skill", "avg_mood", "router"]
