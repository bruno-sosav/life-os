import { api } from '../../lib/api.js'
import { format, subDays } from 'date-fns'

const daysAgoISO = (n) => format(subDays(new Date(), n), 'yyyy-MM-dd')

// ─── Gym ────────────────────────────────────────────────────
// Cada sesión trae sus ejercicios en `exercises`
export const fetchGymSessions = (limit = 50) => api('/gym/sessions', { params: { limit } })

export const createGymSession = ({ date, routine_name, attended = true, notes, exercises = [] }) =>
  api('/gym/sessions', { method: 'POST', body: { date, routine_name, attended, notes, exercises } })

export const updateGymSession = (id, patch) =>
  api(`/gym/sessions/${id}`, { method: 'PATCH', body: patch })

export const deleteGymSession = (id) => api(`/gym/sessions/${id}`, { method: 'DELETE' })

// Un punto por sesión: { date, max_weight_kg, volume_kg }
export const fetchExerciseProgression = (exerciseName) =>
  api('/gym/exercises/progression', { params: { name: exerciseName } })

export const fetchAllExerciseNames = () => api('/gym/exercises/names')

// ─── MMA ────────────────────────────────────────────────────
export const fetchMMASessions = () => api('/mma/sessions')

export const createMMASession = (payload) => api('/mma/sessions', { method: 'POST', body: payload })

export const updateMMASession = (id, patch) =>
  api(`/mma/sessions/${id}`, { method: 'PATCH', body: patch })

export const deleteMMASession = (id) => api(`/mma/sessions/${id}`, { method: 'DELETE' })

// ─── Peso / Nutrición ───────────────────────────────────────
export const fetchWeightLogs = (rangeDays = 90) =>
  api('/weight-logs', { params: { start: daysAgoISO(rangeDays) } })

export const upsertWeightLog = ({ date, weight_kg, notes }) =>
  api(`/weight-logs/${date}`, { method: 'PUT', body: { weight_kg, notes } })

export const fetchNutritionLogs = (rangeDays = 30) =>
  api('/nutrition-logs', { params: { start: daysAgoISO(rangeDays) } })

export const upsertNutritionLog = ({ date, ...payload }) =>
  api(`/nutrition-logs/${date}`, { method: 'PUT', body: payload })
