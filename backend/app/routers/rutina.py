from datetime import date

from fastapi import APIRouter, Response, status
from sqlalchemy import select

from app.db import SessionDep
from app.models import Habit, HabitLog, RoutineBlock, RoutineCompletion, WeeklyReview
from app.routers.common import get_or_404
from app.schemas.rutina import (
    HabitCreate,
    HabitLogOut,
    HabitLogUpsert,
    HabitOut,
    HabitUpdate,
    LinkedModule,
    RoutineBlockIn,
    RoutineBlockOut,
    RoutineCompletionOut,
    RoutineCompletionToggle,
    WeeklyReviewIn,
    WeeklyReviewOut,
)

router = APIRouter(tags=["rutina"])


# ─── Hábitos ────────────────────────────────────────────────
@router.get("/habits", response_model=list[HabitOut])
def list_habits(
    session: SessionDep, active: bool | None = None, linked_module: LinkedModule | None = None
) -> list[Habit]:
    query = select(Habit).order_by(
        Habit.start_time.is_(None), Habit.start_time, Habit.sort_order, Habit.created_at
    )
    if active is not None:
        query = query.where(Habit.active == active)
    if linked_module is not None:
        query = query.where(Habit.linked_module == linked_module)
    return list(session.scalars(query))


@router.post("/habits", response_model=HabitOut, status_code=status.HTTP_201_CREATED)
def create_habit(payload: HabitCreate, session: SessionDep) -> Habit:
    habit = Habit(**payload.model_dump())
    session.add(habit)
    session.commit()
    session.refresh(habit)
    return habit


@router.patch("/habits/{habit_id}", response_model=HabitOut)
def update_habit(habit_id: str, payload: HabitUpdate, session: SessionDep) -> Habit:
    habit = get_or_404(session, Habit, habit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(habit, field, value)
    session.commit()
    return habit


@router.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, Habit, habit_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Logs de hábitos ────────────────────────────────────────
@router.get("/habit-logs", response_model=list[HabitLogOut])
def list_habit_logs(start: date, end: date, session: SessionDep) -> list[HabitLog]:
    query = select(HabitLog).where(HabitLog.date.between(start, end))
    return list(session.scalars(query))


@router.put("/habit-logs", response_model=HabitLogOut)
def upsert_habit_log(payload: HabitLogUpsert, session: SessionDep) -> HabitLog:
    get_or_404(session, Habit, payload.habit_id)
    log = session.scalar(
        select(HabitLog).where(HabitLog.habit_id == payload.habit_id, HabitLog.date == payload.date)
    )
    if log is None:
        log = HabitLog(habit_id=payload.habit_id, date=payload.date)
        session.add(log)
    log.completed = payload.completed
    session.commit()
    session.refresh(log)
    return log


# ─── Bloques de rutina ──────────────────────────────────────
@router.get("/routine-blocks", response_model=list[RoutineBlockOut])
def list_routine_blocks(session: SessionDep) -> list[RoutineBlock]:
    return list(session.scalars(select(RoutineBlock).order_by(RoutineBlock.hour_start)))


@router.post("/routine-blocks", response_model=RoutineBlockOut, status_code=status.HTTP_201_CREATED)
def create_routine_block(payload: RoutineBlockIn, session: SessionDep) -> RoutineBlock:
    block = RoutineBlock(**payload.model_dump())
    session.add(block)
    session.commit()
    return block


@router.put("/routine-blocks/{block_id}", response_model=RoutineBlockOut)
def replace_routine_block(
    block_id: str, payload: RoutineBlockIn, session: SessionDep
) -> RoutineBlock:
    block = get_or_404(session, RoutineBlock, block_id)
    for field, value in payload.model_dump().items():
        setattr(block, field, value)
    session.commit()
    return block


@router.delete("/routine-blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routine_block(block_id: str, session: SessionDep) -> Response:
    session.delete(get_or_404(session, RoutineBlock, block_id))
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Completions de rutina ──────────────────────────────────
@router.get("/routine-completions", response_model=list[RoutineCompletionOut])
def list_routine_completions(date: date, session: SessionDep) -> list[RoutineCompletion]:
    return list(session.scalars(select(RoutineCompletion).where(RoutineCompletion.date == date)))


@router.put("/routine-completions", status_code=status.HTTP_204_NO_CONTENT)
def toggle_routine_completion(payload: RoutineCompletionToggle, session: SessionDep) -> Response:
    """completed=true la registra; completed=false la borra."""
    get_or_404(session, RoutineBlock, payload.block_id)
    completion = session.scalar(
        select(RoutineCompletion).where(
            RoutineCompletion.block_id == payload.block_id, RoutineCompletion.date == payload.date
        )
    )
    if payload.completed and completion is None:
        session.add(RoutineCompletion(block_id=payload.block_id, date=payload.date))
    elif not payload.completed and completion is not None:
        session.delete(completion)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── Cierre semanal ─────────────────────────────────────────
@router.get("/weekly-reviews/{week_start}", response_model=WeeklyReviewOut | None)
def get_weekly_review(week_start: date, session: SessionDep) -> WeeklyReview | None:
    return session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))


@router.put("/weekly-reviews/{week_start}", response_model=WeeklyReviewOut)
def upsert_weekly_review(
    week_start: date, payload: WeeklyReviewIn, session: SessionDep
) -> WeeklyReview:
    review = session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))
    if review is None:
        review = WeeklyReview(week_start=week_start)
        session.add(review)
    review.went_well = payload.went_well
    review.would_change = payload.would_change
    session.commit()
    session.refresh(review)
    return review
