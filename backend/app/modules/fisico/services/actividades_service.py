from typing import Any

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404, unprocessable
from app.modules.fisico.models.actividades_model import Activity
from app.modules.fisico.repositories import actividades_repository
from app.modules.fisico.schemas.actividades_schema import ActivityField, ActivityIn, ActivityUpdate
from app.modules.rutina import Habit


def list_activities(session: Session, active: bool | None = None) -> list[Activity]:
    return actividades_repository.list_activities(session, active)


def _check_habit(session: Session, habit_id: str | None) -> None:
    if habit_id is not None and session.get(Habit, habit_id) is None:
        raise unprocessable("El hábito no existe")


def merge_fields(old: list[dict[str, Any]], new: list[ActivityField]) -> list[dict[str, Any]]:
    """Los campos que ya no vienen quedan archivados: así el historial se sigue leyendo.

    Un campo no puede cambiar de tipo, porque sus valores viejos dejarían de tener sentido.
    """
    previous = {f["id"]: f for f in old}
    for field in new:
        if field.id in previous and previous[field.id]["type"] != field.type:
            raise unprocessable(
                f"'{field.name}' no puede cambiar de tipo: archivalo y creá uno nuevo"
            )
    kept = {f.id for f in new}
    missing = [{**f, "archived": True} for f in old if f["id"] not in kept]
    return [f.model_dump() for f in new] + missing


def create_activity(session: Session, payload: ActivityIn) -> Activity:
    _check_habit(session, payload.habit_id)
    return base_repository.save(session, Activity(**payload.model_dump()))


def update_activity(session: Session, activity_id: str, payload: ActivityUpdate) -> Activity:
    activity = get_or_404(session, Activity, activity_id)
    changes = payload.model_dump(exclude_unset=True)
    if "habit_id" in changes:
        _check_habit(session, changes["habit_id"])
    if payload.fields is None:
        changes.pop("fields", None)
    else:
        changes["fields"] = merge_fields(activity.fields, payload.fields)
    return base_repository.save(session, base_repository.apply(activity, changes))


def delete_activity(session: Session, activity_id: str) -> None:
    """Borra la actividad con todas sus sesiones. Para dejar de verla sin perder nada: pausarla."""
    base_repository.delete(session, get_or_404(session, Activity, activity_id))
