from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.core.errores_util import get_or_404
from app.modules.rutina.models.bloques_model import RoutineBlock, RoutineCompletion
from app.modules.rutina.repositories import bloques_repository
from app.modules.rutina.schemas.bloques_schema import RoutineBlockIn, RoutineCompletionToggle


def list_routine_blocks(session: Session) -> list[RoutineBlock]:
    return bloques_repository.list_routine_blocks(session)


def block_categories(session: Session) -> list[str]:
    return base_repository.used_labels(session, RoutineBlock.category)


def create_routine_block(session: Session, payload: RoutineBlockIn) -> RoutineBlock:
    return base_repository.save(session, RoutineBlock(**payload.model_dump()))


def replace_routine_block(session: Session, block_id: str, payload: RoutineBlockIn) -> RoutineBlock:
    block = get_or_404(session, RoutineBlock, block_id)
    return base_repository.save(session, base_repository.apply(block, payload.model_dump()))


def delete_routine_block(session: Session, block_id: str) -> None:
    base_repository.delete(session, get_or_404(session, RoutineBlock, block_id))


def block_completions(session: Session, start: date, end: date) -> list[tuple[str, date]]:
    return bloques_repository.block_completions(session, start, end)


def toggle_routine_completion(session: Session, payload: RoutineCompletionToggle) -> None:
    """completed=true la registra; completed=false la borra."""
    get_or_404(session, RoutineBlock, payload.block_id)
    completion = bloques_repository.completion_of(session, payload.block_id, payload.date)
    if payload.completed and completion is None:
        base_repository.save(
            session, RoutineCompletion(block_id=payload.block_id, date=payload.date)
        )
    elif not payload.completed and completion is not None:
        base_repository.delete(session, completion)
