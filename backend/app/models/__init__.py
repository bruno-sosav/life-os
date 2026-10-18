"""Modelos ORM. Importarlos acá registra todas las tablas en Base.metadata (lo usa Alembic)."""

from app.models.finanzas import FinanceExpense, FinanceIncome
from app.models.fisico import GymExercise, GymSession, MmaSession, NutritionLog, WeightLog
from app.models.listas import ListItem, PersonalList
from app.models.mental import Book, Idea, JournalEntry, MoodLog
from app.models.negocio import Project, StratusGoal, StratusIdea, StratusTask
from app.models.rutina import Habit, HabitLog, RoutineBlock, RoutineCompletion, WeeklyReview

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
    "ListItem",
    "MmaSession",
    "MoodLog",
    "NutritionLog",
    "PersonalList",
    "Project",
    "RoutineBlock",
    "RoutineCompletion",
    "StratusGoal",
    "StratusIdea",
    "StratusTask",
    "WeeklyReview",
    "WeightLog",
]
