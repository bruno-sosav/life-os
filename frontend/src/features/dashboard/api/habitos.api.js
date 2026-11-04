import { api } from '../../../shared/lib/api.js'

export const createHabit = (payload) => api('/habits', { method: 'POST', body: payload })
export const updateHabit = (id, patch) => api(`/habits/${id}`, { method: 'PATCH', body: patch })
export const deleteHabit = (id) => api(`/habits/${id}`, { method: 'DELETE' })
export const toggleHabitLog = ({ habit_id, date, completed }) =>
  api('/habit-logs', { method: 'PUT', body: { habit_id, date, completed } })
