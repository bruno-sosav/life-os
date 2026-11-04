from collections.abc import Iterable, Sequence
from datetime import date
from typing import Literal

import pandas as pd

from app.modules.rutina.models.bloques_model import RoutineBlock
from app.modules.rutina.models.habitos_model import Habit

STREAK_THRESHOLD = 0.7  # un día se cumple con al menos el 70 % de lo agendado

STREAK_WINDOW_DAYS = 90  # la racha y el mapa de Stats miran estos días hacia atrás

DayStatus = Literal["cumplido", "parcial", "sin_cumplir", "libre", "pendiente"]


def _exists_on(record: Habit | RoutineBlock, day: date) -> bool:
    """Lo creado después de `day` no cuenta ese día: sumar un hábito no baja el pasado.

    shortcut: created_at está en UTC, así que algo creado después de las 21 h (UTC-3) cuenta
    recién desde el día siguiente; guardar la fecha local de creación si eso molesta.
    """
    return record.created_at is None or record.created_at.date() <= day


def habit_runs_on(habit: Habit, dow: int) -> bool:
    return not habit.days_of_week or dow in habit.days_of_week


def block_runs_on(block: RoutineBlock, day: date) -> bool:
    if not block.repeat_weekly:
        return block.specific_date == day
    return day.weekday() in (block.days_of_week or [])


def scheduled_on(item: Habit | RoutineBlock, day: date) -> bool:
    """¿Estaba agendado ese día? Los semanales, desde que se crearon; un bloque puntual, siempre."""
    if isinstance(item, RoutineBlock):
        return block_runs_on(item, day) and (not item.repeat_weekly or _exists_on(item, day))
    return habit_runs_on(item, day.weekday()) and _exists_on(item, day)


def expected_per_day(
    days: pd.DatetimeIndex, blocks: Sequence[RoutineBlock], habits: Sequence[Habit]
) -> pd.Series:
    """Cantidad de bloques + hábitos agendados para cada día."""
    items: list[Habit | RoutineBlock] = [*blocks, *habits]
    values = [sum(scheduled_on(i, day) for i in items) for day in (d.date() for d in days)]
    return pd.Series(values, index=days, dtype="int64")


def done_per_day(
    days: pd.DatetimeIndex,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done: Iterable[tuple[str, date]],
) -> pd.Series:
    """Cuántos de los agendados de cada día se hicieron. `done` son pares (id, fecha).

    Lo que no estaba agendado ese día (un hábito marcado en otro día, la marca vieja de un
    bloque al que le cambiaron los días) no suma: si no, tapa lo que faltó.
    """
    scheduled: list[Habit | RoutineBlock] = [*blocks, *habits]
    items = {i.id: i for i in scheduled}
    dates = [day for item_id, day in done if item_id in items and scheduled_on(items[item_id], day)]
    counts = pd.Series(pd.to_datetime(dates), dtype="datetime64[ns]").value_counts()
    return counts.reindex(days, fill_value=0).astype("int64")


def day_status(
    today: date,
    days: pd.DatetimeIndex,
    blocks: Sequence[RoutineBlock],
    habits: Sequence[Habit],
    done: Iterable[tuple[str, date]],
) -> pd.Series:
    """Estado de cada día con la regla del 70 %. Hoy, si todavía no llegó, queda 'pendiente'."""
    expected = expected_per_day(days, blocks, habits)
    done = done_per_day(days, blocks, habits, done)
    ratio = done / expected.where(expected > 0)
    status = pd.Series("sin_cumplir", index=days, dtype="object")
    status[done > 0] = "parcial"
    status[ratio >= STREAK_THRESHOLD] = "cumplido"
    status[expected == 0] = "libre"
    status[(status.index == pd.Timestamp(today)) & (status != "cumplido") & (status != "libre")] = (
        "pendiente"
    )
    return status


def streaks(status: pd.Series) -> tuple[int, int]:
    """(racha actual, mejor racha) de días cumplidos seguidos. Libres y hoy pendiente no cortan."""
    ok = status[~status.isin(["libre", "pendiente"])] == "cumplido"
    if ok.empty:
        return 0, 0
    runs = ok.groupby((~ok).cumsum()).cumsum()  # largo de la racha que termina en cada día
    return int(runs.iloc[-1]), int(runs.max())
