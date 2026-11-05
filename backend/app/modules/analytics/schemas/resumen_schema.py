import datetime as dt

from pydantic import BaseModel

from app.modules.analytics.schemas.cumplimiento_schema import Compliance, CompliancePoint
from app.modules.analytics.schemas.indicadores_schema import (
    HabitsByWeek,
    KPIs,
    RadarAxis,
    SkillsByWeek,
)
from app.modules.analytics.schemas.series_schema import (
    ActivityCount,
    FinanceMonth,
    WeightPoint,
)


class AnalyticsSummary(BaseModel):
    week_start: dt.date
    week_end: dt.date
    compliance: Compliance
    compliance_history: list[CompliancePoint]
    kpis: KPIs
    habits_by_week: HabitsByWeek
    radar: list[RadarAxis]
    weight_series: list[WeightPoint]
    skills_by_week: SkillsByWeek
    activity_distribution: list[ActivityCount]
    finance_monthly: list[FinanceMonth]
