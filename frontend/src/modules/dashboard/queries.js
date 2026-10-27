import { api } from '../../lib/api.js'
import { todayISO } from '../../lib/dates.js'

// ─── Agenda del día (secciones, estado y progreso calculados en el backend) ─
export const fetchAgenda = (dateISO) =>
  api('/dashboard/agenda', { params: { date: dateISO, today: todayISO() } })

export async function fetchGlobalStreak() {
  const { streak } = await api('/dashboard/streak', { params: { today: todayISO() } })
  return streak
}

// ─── Hábitos ────────────────────────────────────────────────
export const createHabit = (payload) => api('/habits', { method: 'POST', body: payload })
export const updateHabit = (id, patch) => api(`/habits/${id}`, { method: 'PATCH', body: patch })
export const deleteHabit = (id) => api(`/habits/${id}`, { method: 'DELETE' })

export const toggleHabitLog = ({ habit_id, date, completed }) =>
  api('/habit-logs', { method: 'PUT', body: { habit_id, date, completed } })

// ─── Bloques de rutina ──────────────────────────────────────
export function upsertRoutineBlock({ id, ...payload }) {
  return id
    ? api(`/routine-blocks/${id}`, { method: 'PUT', body: payload })
    : api('/routine-blocks', { method: 'POST', body: payload })
}

export const deleteRoutineBlock = (id) => api(`/routine-blocks/${id}`, { method: 'DELETE' })

export const toggleRoutineCompletion = ({ block_id, date, completed }) =>
  api('/routine-completions', { method: 'PUT', body: { block_id, date, completed } })

// ─── Cierre semanal (estadísticas + revisión guardada) ──────
export const fetchWeeklyReview = () =>
  api('/dashboard/weekly-review', { params: { today: todayISO() } })

export const saveWeeklyReview = ({ week_start, went_well, would_change }) =>
  api(`/weekly-reviews/${week_start}`, { method: 'PUT', body: { went_well, would_change } })
