from datetime import date

from sqlalchemy.orm import Session

from app.core.database import base_repository
from app.modules.rutina.models.revisiones_model import WeeklyReview
from app.modules.rutina.repositories import revisiones_repository
from app.modules.rutina.schemas.revisiones_schema import WeeklyReviewIn


def get_weekly_review(session: Session, week_start: date) -> WeeklyReview | None:
    return revisiones_repository.weekly_review_of(session, week_start)


def upsert_weekly_review(
    session: Session, week_start: date, payload: WeeklyReviewIn
) -> WeeklyReview:
    review = revisiones_repository.weekly_review_of(session, week_start) or WeeklyReview(
        week_start=week_start
    )
    review.went_well = payload.went_well
    review.would_change = payload.would_change
    return base_repository.save(session, review)
