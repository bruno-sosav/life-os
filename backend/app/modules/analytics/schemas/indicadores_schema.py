from pydantic import BaseModel


class KPIs(BaseModel):
    current_streak: int
    best_streak: int
    workouts_month: int
    habit_month_pct: int
    last_weight: float | None
    weight_trend: float | None  # kg contra el último registro de hace 30+ días
    year: int
    books_year: int


class HabitRef(BaseModel):
    id: str
    name: str
    color: str | None


class HabitsByWeek(BaseModel):
    habits: list[HabitRef]
    # Una fila por semana: {"week_start": "...", "<habit_id>": completados, ...}
    weeks: list[dict[str, int | str]]


class SkillRef(BaseModel):
    id: str
    name: str


class SkillsByWeek(BaseModel):
    skills: list[SkillRef]
    # Una fila por semana: {"week_start": "...", "<skill_id>": minutos, ...}
    weeks: list[dict[str, int | str]]


class RadarAxis(BaseModel):
    axis: str
    semana: int
    anterior: int
