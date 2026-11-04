import math
from typing import Any

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404, unprocessable
from app.modules.fisico.models.actividades_model import Activity
from app.modules.fisico.models.sesiones_model import ActivitySession, SessionExercise
from app.modules.fisico.repositories import sesiones_repository
from app.modules.fisico.schemas.actividades_schema import CHARTABLE
from app.modules.fisico.schemas.sesiones_schema import ProgressionPoint, SessionIn

MAX_TEXT = 2000


def _check_value(field: dict[str, Any], value: Any) -> Any:
    kind = field["type"]
    is_number = isinstance(value, int | float) and not isinstance(value, bool)
    valid = {
        "numero": is_number and math.isfinite(value),
        "texto": isinstance(value, str) and len(value) <= MAX_TEXT,
        "si_no": isinstance(value, bool),
        "opcion": value in (field["options"] or []),
        "escala": is_number and value in (1, 2, 3, 4, 5),
    }.get(kind, False)
    if not valid:
        raise unprocessable(f"Valor inválido para '{field['name']}'")
    if kind == "numero":
        return float(value)
    return int(value) if kind == "escala" else value


def clean_values(fields: list[dict[str, Any]], values: dict[str, Any]) -> dict[str, Any]:
    """Valida cada valor contra su campo. Un valor vacío (None o "") no se guarda."""
    by_id = {f["id"]: f for f in fields if not f["archived"] and f["type"] != "ejercicios"}
    clean = {}
    for field_id, value in values.items():
        if field_id not in by_id:
            raise unprocessable(f"La actividad no tiene el campo {field_id}")
        if value is not None and value != "":
            clean[field_id] = _check_value(by_id[field_id], value)
    return clean


def _has_exercises(activity: Activity) -> bool:
    return any(f["type"] == "ejercicios" and not f["archived"] for f in activity.fields)


def list_sessions(session: Session, activity_id: str | None, limit: int) -> list[ActivitySession]:
    return sesiones_repository.list_sessions(session, activity_id, limit)


def create_session(session: Session, payload: SessionIn) -> ActivitySession:
    """Crea la sesión y sus ejercicios en una sola transacción."""
    activity = session.get(Activity, payload.activity_id)
    if activity is None:
        raise unprocessable("La actividad no existe")
    if payload.exercises and not _has_exercises(activity):
        raise unprocessable(f"'{activity.name}' no tiene lista de ejercicios")
    record = ActivitySession(
        **payload.model_dump(exclude={"values", "exercises"}),
        values=clean_values(activity.fields, payload.values),
    )
    record.exercises = [SessionExercise(**e.model_dump()) for e in payload.exercises]
    return base_repository.save(session, record)


def delete_session(session: Session, session_id: str) -> None:
    base_repository.delete(session, get_or_404(session, ActivitySession, session_id))


def list_exercise_names(session: Session, activity_id: str) -> list[str]:
    return sesiones_repository.list_exercise_names(session, activity_id)


def exercise_progression(session: Session, activity_id: str, name: str) -> list[ProgressionPoint]:
    rows = sesiones_repository.exercise_progression(session, activity_id, name.strip().lower())
    return [
        ProgressionPoint(date=day, value=float(kg) if kg is not None else None) for day, kg in rows
    ]


def field_series(session: Session, activity_id: str, field_id: str) -> list[ProgressionPoint]:
    """Un punto por sesión con valor en ese campo (número o escala), en orden de fecha."""
    activity = get_or_404(session, Activity, activity_id)
    field = next((f for f in activity.fields if f["id"] == field_id), None)
    if field is None or field["type"] not in CHARTABLE:
        raise unprocessable("Ese campo no se puede graficar")
    return [
        ProgressionPoint(date=day, value=float(values[field_id]))
        for day, values in sesiones_repository.field_values(session, activity.id)
        if isinstance(values.get(field_id), int | float)
    ]
