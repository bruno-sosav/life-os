from datetime import date

from fastapi import APIRouter, Response, status

from app.core.database.conexion_database import SessionDep
from app.modules.rutina import rutina_service as service
from app.modules.rutina.rutina_model import (
    Habit,
    HabitLog,
    RoutineBlock,
    RoutineCompletion,
    WeeklyReview,
)
from app.modules.rutina.rutina_schema import (
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
CREATED = status.HTTP_201_CREATED
NO_CONTENT = status.HTTP_204_NO_CONTENT


@router.get("/habits", response_model=list[HabitOut])
def list_habits(
    session: SessionDep, active: bool | None = None, linked_module: LinkedModule | None = None
) -> list[Habit]:
    return service.list_habits(session, active, linked_module)


@router.post("/habits", response_model=HabitOut, status_code=CREATED)
def create_habit(payload: HabitCreate, session: SessionDep) -> Habit:
    return service.create_habit(session, payload)


@router.patch("/habits/{habit_id}", response_model=HabitOut)
def update_habit(habit_id: str, payload: HabitUpdate, session: SessionDep) -> Habit:
    return service.update_habit(session, habit_id, payload)


@router.delete("/habits/{habit_id}", status_code=NO_CONTENT)
def delete_habit(habit_id: str, session: SessionDep) -> Response:
    service.delete_habit(session, habit_id)
    return Response(status_code=NO_CONTENT)


@router.get("/habit-logs", response_model=list[HabitLogOut])
def list_habit_logs(start: date, end: date, session: SessionDep) -> list[HabitLog]:
    return service.list_habit_logs(session, start, end)


@router.put("/habit-logs", response_model=HabitLogOut)
def upsert_habit_log(payload: HabitLogUpsert, session: SessionDep) -> HabitLog:
    return service.upsert_habit_log(session, payload)


@router.get("/routine-blocks", response_model=list[RoutineBlockOut])
def list_routine_blocks(session: SessionDep) -> list[RoutineBlock]:
    return service.list_routine_blocks(session)


@router.post("/routine-blocks", response_model=RoutineBlockOut, status_code=CREATED)
def create_routine_block(payload: RoutineBlockIn, session: SessionDep) -> RoutineBlock:
    return service.create_routine_block(session, payload)


@router.put("/routine-blocks/{block_id}", response_model=RoutineBlockOut)
def replace_routine_block(
    block_id: str, payload: RoutineBlockIn, session: SessionDep
) -> RoutineBlock:
    return service.replace_routine_block(session, block_id, payload)


@router.delete("/routine-blocks/{block_id}", status_code=NO_CONTENT)
def delete_routine_block(block_id: str, session: SessionDep) -> Response:
    service.delete_routine_block(session, block_id)
    return Response(status_code=NO_CONTENT)


@router.get("/routine-completions", response_model=list[RoutineCompletionOut])
def list_routine_completions(date: date, session: SessionDep) -> list[RoutineCompletion]:
    return service.list_routine_completions(session, date)


@router.put("/routine-completions", status_code=NO_CONTENT)
def toggle_routine_completion(payload: RoutineCompletionToggle, session: SessionDep) -> Response:
    service.toggle_routine_completion(session, payload)
    return Response(status_code=NO_CONTENT)


@router.get("/weekly-reviews/{week_start}", response_model=WeeklyReviewOut | None)
def get_weekly_review(week_start: date, session: SessionDep) -> WeeklyReview | None:
    return service.get_weekly_review(session, week_start)


@router.put("/weekly-reviews/{week_start}", response_model=WeeklyReviewOut)
def upsert_weekly_review(
    week_start: date, payload: WeeklyReviewIn, session: SessionDep
) -> WeeklyReview:
    return service.upsert_weekly_review(session, week_start, payload)
