from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.rutina.models.revisiones_model import WeeklyReview


def weekly_review_of(session: Session, week_start: date) -> WeeklyReview | None:
    return session.scalar(select(WeeklyReview).where(WeeklyReview.week_start == week_start))
