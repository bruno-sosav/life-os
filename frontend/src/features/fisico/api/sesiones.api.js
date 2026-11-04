import { api } from '../../../shared/lib/api.js'

// Cada sesión trae `values` ({ field_id: valor }) y `exercises`; sin activityId, de todos los tipos
export const fetchSessions = (activityId, limit = 50) =>
  api('/sessions', { params: { activity_id: activityId, limit } })
export const createSession = (payload) => api('/sessions', { method: 'POST', body: payload })
export const deleteSession = (id) => api(`/sessions/${id}`, { method: 'DELETE' })

// Ejercicios de cualquier tipo, sin distinguir mayúsculas
export const fetchExerciseNames = () => api('/exercises/names')
export const fetchLastExercise = (name) => api('/exercises/last', { params: { name } })
// { points: [{ date, value }], best }
export const fetchExerciseProgression = (name) => api('/exercises/progression', { params: { name } })
export const fetchFieldSeries = (activityId, fieldId) =>
  api(`/activities/${activityId}/fields/${fieldId}/series`)
