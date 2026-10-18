import { api } from '../../lib/api.js'
import { todayISO } from '../../lib/dates.js'
import { format, startOfWeek, addDays, subWeeks } from 'date-fns'

// ─── Hábitos ────────────────────────────────────────────────
export async function fetchLinkedModuleHabit(module) {
  try {
    const habits = await api('/habits', { params: { active: true, linked_module: module } })
    return habits[0] ?? null
  } catch { return null }
}

export const fetchActiveHabits = () => api('/habits', { params: { active: true } })

export const createHabit = (payload) => api('/habits', { method: 'POST', body: payload })

export const updateHabit = (id, patch) => api(`/habits/${id}`, { method: 'PATCH', body: patch })

export const deleteHabit = (id) => api(`/habits/${id}`, { method: 'DELETE' })

export const fetchHabitLogsRange = (startISO, endISO) =>
  api('/habit-logs', { params: { start: startISO, end: endISO } })

export const toggleHabitLog = ({ habit_id, date, completed }) =>
  api('/habit-logs', { method: 'PUT', body: { habit_id, date, completed } })

// ─── Routine blocks ──────────────────────────────────────────
export const fetchRoutineBlocks = () => api('/routine-blocks')

export function upsertRoutineBlock({ id, ...payload }) {
  return id
    ? api(`/routine-blocks/${id}`, { method: 'PUT', body: payload })
    : api('/routine-blocks', { method: 'POST', body: payload })
}

export const deleteRoutineBlock = (id) => api(`/routine-blocks/${id}`, { method: 'DELETE' })

// ─── Routine completions ────────────────────────────────────
export const fetchRoutineCompletions = (dateISO) =>
  api('/routine-completions', { params: { date: dateISO } })

export const toggleRoutineCompletion = ({ block_id, date, completed }) =>
  api('/routine-completions', { method: 'PUT', body: { block_id, date, completed } })

// ─── Racha global (calculada en el backend) ─────────────────
export async function fetchGlobalStreak() {
  const { streak } = await api('/dashboard/streak', { params: { today: todayISO() } })
  return streak
}

// ─── Cierre semanal ──────────────────────────────────────────
export function getWeekBounds(offsetWeeks = 0) {
  const monday = startOfWeek(subWeeks(new Date(), offsetWeeks), { weekStartsOn: 1 })
  return { start: format(monday, 'yyyy-MM-dd'), end: format(addDays(monday, 6), 'yyyy-MM-dd') }
}

export const fetchWeeklyReviewStats = (weekStart) =>
  api('/dashboard/weekly-stats', { params: { week_start: weekStart, today: todayISO() } })

export const fetchWeeklyReview = (weekStart) => api(`/weekly-reviews/${weekStart}`)

export const saveWeeklyReview = ({ week_start, went_well, would_change }) =>
  api(`/weekly-reviews/${week_start}`, { method: 'PUT', body: { went_well, would_change } })
