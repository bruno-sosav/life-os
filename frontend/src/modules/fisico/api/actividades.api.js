import { api } from '../../../lib/api.js'

// Los tipos de entrenamiento. Campo: { id, name, type, unit, options, archived }
export const fetchActivities = () => api('/activities')
export const createActivity = (payload) => api('/activities', { method: 'POST', body: payload })
// `fields` es la lista completa: un campo que no viene queda archivado (no se borra)
export const updateActivity = (id, patch) => api(`/activities/${id}`, { method: 'PATCH', body: patch })
// Borra también todas sus sesiones. Para dejar de verlo sin perder nada: pausarlo.
export const deleteActivity = (id) => api(`/activities/${id}`, { method: 'DELETE' })
// Para elegir el hábito vinculado: entrenar lo marca en el dashboard
export const fetchActiveHabits = () => api('/habits', { params: { active: true } })
