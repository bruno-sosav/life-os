"""Modelos ORM. Importarlos acá registra todas las tablas en Base.metadata (lo usa Alembic)."""

from app.models.usuario import User
from app.modules.finanzas import FinanceExpense, FinanceIncome
from app.modules.fisico import GymExercise, GymSession, MmaSession, NutritionLog, WeightLog
from app.modules.mental import Book, Idea, JournalEntry, MoodLog
from app.modules.negocio import Project, StratusGoal, StratusIdea, StratusTask
from app.modules.rutina import Habit, HabitLog, RoutineBlock, RoutineCompletion, WeeklyReview

__all__ = [
    "Book",
    "FinanceExpense",
    "FinanceIncome",
    "GymExercise",
    "GymSession",
    "Habit",
    "HabitLog",
    "Idea",
    "JournalEntry",
    "MmaSession",
    "MoodLog",
    "NutritionLog",
    "Project",
    "RoutineBlock",
    "RoutineCompletion",
    "StratusGoal",
    "StratusIdea",
    "StratusTask",
    "User",
    "WeeklyReview",
    "WeightLog",
]
