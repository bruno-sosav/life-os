from datetime import date

from pydantic import BaseModel, Field, model_validator

from app.core.base_schema import Label, ORMModel
from app.modules.rutina.schemas.habitos_schema import DayOfWeek


class RoutineBlockFields(BaseModel):
    days_of_week: list[DayOfWeek] | None = None
    specific_date: date | None = None
    repeat_weekly: bool = True
    hour_start: int = Field(ge=0, le=23)
    hour_min: int = Field(default=0, ge=0, le=59)
    hour_end: int = Field(ge=0, le=23)
    activity: str = Field(min_length=1, max_length=255)
    category: Label | None = None
    emoji: str | None = None
    color: str | None = None


class RoutineBlockIn(RoutineBlockFields):
    @model_validator(mode="after")
    def normalize_schedule(self) -> "RoutineBlockIn":
        """Semanal: al menos un día. Puntual: fecha."""
        if self.repeat_weekly:
            if not self.days_of_week:
                raise ValueError("Un bloque semanal necesita al menos un día")
            self.days_of_week = sorted(set(self.days_of_week))
            self.specific_date = None
        else:
            if self.specific_date is None:
                raise ValueError("Un bloque de un solo día necesita la fecha")
            self.days_of_week = None
        return self


class RoutineBlockOut(RoutineBlockFields, ORMModel):
    id: str


class RoutineCompletionToggle(BaseModel):
    block_id: str
    date: date
    completed: bool
