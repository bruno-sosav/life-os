"""Mental: libros, mood diario, diario personal e ideas. Es lo único que ven los otros módulos."""

from fastapi import APIRouter

from app.modules.mental.controllers import (
    diario_controller,
    ideas_controller,
    libros_controller,
    mood_controller,
)
from app.modules.mental.models.diario_model import JournalEntry
from app.modules.mental.models.ideas_model import Idea
from app.modules.mental.models.libros_model import Book
from app.modules.mental.models.mood_model import MoodLog
from app.modules.mental.services.mood_service import avg_mood

router = APIRouter(tags=["mental"])
for controller in (libros_controller, mood_controller, diario_controller, ideas_controller):
    router.include_router(controller.router)

__all__ = ["Book", "Idea", "JournalEntry", "MoodLog", "avg_mood", "router"]
