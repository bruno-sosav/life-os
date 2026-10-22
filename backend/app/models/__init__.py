"""Modelos ORM. Importarlos acá registra todas las tablas en Base.metadata (lo usa Alembic)."""

from app.models.fisico import GymExercise, GymSession, MmaSession, NutritionLog, WeightLog
from app.models.mental import Book, Idea, JournalEntry, MoodLog
from app.models.negocio import Project, StratusGoal, StratusIdea, StratusTask
from app.models.rutina import Habit, HabitLog, RoutineBlock, RoutineCompletion, WeeklyReview
from app.models.usuario import User
from app.modules.finanzas import FinanceExpense, FinanceIncome

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
