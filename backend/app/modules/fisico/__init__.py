"""Físico: gimnasio (sesiones y ejercicios), MMA, peso y nutrición."""

from app.modules.fisico.fisico_controller import router
from app.modules.fisico.fisico_model import (
    GymExercise,
    GymSession,
    MmaSession,
    NutritionLog,
    WeightLog,
)

__all__ = ["GymExercise", "GymSession", "MmaSession", "NutritionLog", "WeightLog", "router"]
