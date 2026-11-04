from datetime import date
from typing import Any

from fastapi import APIRouter

from app.core.database.conexion_database import SessionDep
from app.modules.dashboard.schemas.agenda_schema import AgendaOut
from app.modules.dashboard.services import agenda_service

router = APIRouter()


@router.get("/agenda", response_model=AgendaOut)
def get_agenda(date: date, today: date, session: SessionDep) -> dict[str, Any]:
    """Agenda de `date`: secciones con bloques y hábitos ordenados, y el progreso del día."""
    return agenda_service.get_agenda(session, date, today)
