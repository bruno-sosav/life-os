import { api } from '../../lib/api.js'
import { format, subDays } from 'date-fns'
import { todayISO } from '../../lib/dates.js'

const daysAgoISO = (n) => format(subDays(new Date(), n), 'yyyy-MM-dd')

// ─── Actividades (las definís vos, con sus campos) ──────────
// Campo: { id, name, type, unit, options, archived }
// type: 'numero' | 'texto' | 'si_no' | 'opcion' | 'escala' | 'ejercicios'
export const fetchActivities = () => api('/activities')

export const createActivity = (payload) => api('/activities', { method: 'POST', body: payload })

// `fields` es la lista completa: un campo que no viene queda archivado (no se borra)
export const updateActivity = (id, patch) =>
  api(`/activities/${id}`, { method: 'PATCH', body: patch })

// Borra también todas sus sesiones. Para dejar de verla sin perder nada: pausarla.
export const deleteActivity = (id) => api(`/activities/${id}`, { method: 'DELETE' })

// Para elegir el hábito vinculado (la asistencia se marca en ese hábito)
export const fetchActiveHabits = () => api('/habits', { params: { active: true } })

// ─── Sesiones ───────────────────────────────────────────────
// Cada sesión trae `values` ({ field_id: valor }) y `exercises`
export const fetchSessions = (activityId, limit = 50) =>
  api('/sessions', { params: { activity_id: activityId, limit } })

export const createSession = (payload) => api('/sessions', { method: 'POST', body: payload })

export const deleteSession = (id) => api(`/sessions/${id}`, { method: 'DELETE' })

// ─── Asistencia y calendario ────────────────────────────────
// Sale del hábito vinculado si hay uno; si no, de las sesiones. { habit, days: [{ date, attended }] }
export const fetchAttendanceWeek = (activityId) =>
  api(`/activities/${activityId}/week`, { params: { today: todayISO() } })

// Alterna la asistencia del día; devuelve { date, attended }
export const toggleAttendance = (activityId, dateISO) =>
  api(`/activities/${activityId}/attendance/${dateISO}`, { method: 'PUT' })

// { count, days: [{ date, attended: true | false | null }] }
export const fetchActivityMonth = (activityId, monthISO) =>
  api(`/activities/${activityId}/month`, { params: { month: monthISO } })

// ─── Gráficos: un punto por sesión, [{ date, value }] ───────
export const fetchExerciseNames = (activityId) => api(`/activities/${activityId}/exercises/names`)

export const fetchExerciseProgression = (activityId, name) =>
  api(`/activities/${activityId}/exercises/progression`, { params: { name } })

export const fetchFieldSeries = (activityId, fieldId) =>
  api(`/activities/${activityId}/fields/${fieldId}/series`)

// ─── Peso / Nutrición ───────────────────────────────────────
export const fetchWeightLogs = (rangeDays = 90) =>
  api('/weight-logs', { params: { start: daysAgoISO(rangeDays) } })

export const fetchWeightGoal = () => api('/weight-goal')
export const saveWeightGoal = (weight_kg) => api('/weight-goal', { method: 'PUT', body: { weight_kg } })

export const upsertWeightLog = ({ date, weight_kg, notes }) =>
  api(`/weight-logs/${date}`, { method: 'PUT', body: { weight_kg, notes } })

export const fetchNutritionLogs = (rangeDays = 30) =>
  api('/nutrition-logs', { params: { start: daysAgoISO(rangeDays) } })

export const upsertNutritionLog = ({ date, ...payload }) =>
  api(`/nutrition-logs/${date}`, { method: 'PUT', body: payload })

// { avg_quality } de los últimos 7 días, o null sin registros
export const fetchNutritionAverage = () =>
  api('/nutrition-logs/average', { params: { today: todayISO() } })
