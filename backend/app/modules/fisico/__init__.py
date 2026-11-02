"""Físico: actividades que definís vos (con sus campos y sesiones), peso y nutrición."""

from app.modules.fisico.fisico_controller import router
from app.modules.fisico.fisico_model import (
    Activity,
    ActivitySession,
    NutritionLog,
    SessionExercise,
    WeightLog,
)
from app.modules.fisico.fisico_service import attended_days, list_activities

__all__ = [
    "Activity",
    "ActivitySession",
    "NutritionLog",
    "SessionExercise",
    "WeightLog",
    "attended_days",
    "list_activities",
    "router",
]
