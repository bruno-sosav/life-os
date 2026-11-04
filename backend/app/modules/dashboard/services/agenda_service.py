from collections.abc import Sequence
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.core.fechas_util import days_between, week_bounds
from app.core.numeros_util import js_round
from app.modules.rutina import (
    Habit,
    RoutineBlock,
    block_completions,
    block_runs_on,
    completed_habit_logs,
    habit_runs_on,
    list_habits,
    list_routine_blocks,
    scheduled_on,
)

SECTIONS = (  # (clave, título, minuto desde, minuto hasta)
    ("manana", "Mañana", 0, 12 * 60),
    ("tarde", "Tarde", 12 * 60, 20 * 60),
    ("noche", "Noche", 20 * 60, 24 * 60),
)


def _start_minutes(item: RoutineBlock | Habit) -> int | None:
    if isinstance(item, RoutineBlock):
        return item.hour_start * 60 + (item.hour_min or 0)
    if item.start_time is None:
        return None
    return item.start_time.hour * 60 + item.start_time.minute


def _on_agenda(item: RoutineBlock | Habit, day: date, today: date) -> bool:
    if day < today:
        return scheduled_on(item, day)
    if isinstance(item, RoutineBlock):
        return block_runs_on(item, day)
    return habit_runs_on(item, day.weekday())


def week_days(today: date) -> list[dict[str, Any]]:
    days = days_between(week_bounds(today))
    return [{"date": d, "weekday": d.weekday(), "is_today": d == today} for d in days]


def agenda(
    day: date,
    today: date,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done_block_ids: set[str],
    done_habit_ids: set[str],
) -> dict[str, Any]:
    """Bloques y hábitos de `day`, ordenados por hora y agrupados por momento del día.

    Un día pasado muestra lo que estaba agendado entonces (lo mismo que cuenta la racha).
    Hoy y los días futuros muestran todo, también lo recién creado.
    """
    done_ids = done_block_ids | done_habit_ids
    entries: list[tuple[int | None, dict[str, Any]]] = []
    items: list[RoutineBlock | Habit] = [*blocks, *habits]
    for item in items:
        if _on_agenda(item, day, today):
            entries.append((_start_minutes(item), _agenda_item(item, item.id in done_ids)))
    # Primero los que tienen hora (por hora); al final los sin horario. Orden estable.
    entries.sort(key=lambda e: (e[0] is None, e[0] or 0))

    sections = [
        {
            "key": key,
            "label": label,
            "items": [it for m, it in entries if m is not None and lo <= m < hi],
        }
        for key, label, lo, hi in SECTIONS
    ]
    sections.append(
        {
            "key": "sin_horario",
            "label": "Sin horario",
            "items": [it for m, it in entries if m is None],
        }
    )
    total = len(entries)
    completed = sum(1 for _, it in entries if it["done"])
    return {
        "date": day,
        "weekday": day.weekday(),
        "week": week_days(today),
        "sections": [s for s in sections if s["items"]],
        "completed": completed,
        "total": total,
        "pct": js_round(completed / total * 100) if total else 0,
    }


def _agenda_item(item: RoutineBlock | Habit, done: bool) -> dict[str, Any]:
    minutes = _start_minutes(item)
    fields: dict[str, Any] = {
        "id": item.id,
        "emoji": item.emoji,
        "color": item.color,
        "time": None if minutes is None else f"{minutes // 60:02d}:{minutes % 60:02d}",
        "done": done,
    }
    if isinstance(item, RoutineBlock):
        return {
            **fields,
            "kind": "block",
            "title": item.activity,
            "category": item.category,
            "block": item,
        }
    return {**fields, "kind": "habit", "title": item.name, "category": None, "habit": item}


def get_agenda(session: Session, day: date, today: date) -> dict[str, Any]:
    return agenda(
        day,
        today,
        list_routine_blocks(session),
        list_habits(session, active=True),
        {block_id for block_id, _ in block_completions(session, day, day)},
        {habit_id for habit_id, _ in completed_habit_logs(session, day, day)},
    )
