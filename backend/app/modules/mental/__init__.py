"""Mental: skills que practicás, listas libres, libros, ideas y el mood del día.

Es lo único que ven los otros módulos.
"""

from fastapi import APIRouter

from app.modules.mental.controllers import (
    ideas_controller,
    libros_controller,
    listas_controller,
    mood_controller,
    practicas_controller,
    recursos_controller,
    skills_controller,
)
from app.modules.mental.models.libros_model import Book
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
    libros_controller,
    ideas_controller,
    mood_controller,
):
    router.include_router(controller.router)

__all__ = ["Book", "MoodLog", "Practice", "Skill", "avg_mood", "router"]
