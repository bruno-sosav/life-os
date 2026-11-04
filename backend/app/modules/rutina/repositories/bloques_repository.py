from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.rutina.models.bloques_model import RoutineBlock, RoutineCompletion


def list_routine_blocks(session: Session) -> list[RoutineBlock]:
    return list(session.scalars(select(RoutineBlock).order_by(RoutineBlock.hour_start)))


def block_completions(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    """(block_id, fecha) de cada bloque cumplido en el rango."""
    query = select(RoutineCompletion.block_id, RoutineCompletion.date).where(
        RoutineCompletion.date.between(start, end)
    )
    return [(block_id, day) for block_id, day in session.execute(query)]


def completion_of(session: Session, block_id: str, day: date) -> RoutineCompletion | None:
    return session.scalar(
        select(RoutineCompletion).where(
            RoutineCompletion.block_id == block_id, RoutineCompletion.date == day
        )
    )
