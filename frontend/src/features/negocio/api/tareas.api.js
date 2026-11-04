import { api } from '../../../shared/lib/api.js'

// El tablero llega por columna y en el orden en que quedaron; completed_at lo maneja el backend
export const fetchBoard = (projectId) => api('/tasks/board', { params: { project_id: projectId } })
export const createTask = (payload) => api('/tasks', { method: 'POST', body: payload })
export const updateTask = (id, patch) => api(`/tasks/${id}`, { method: 'PATCH', body: patch })
export const moveTask = (id, status, position) =>
  api(`/tasks/${id}/move`, { method: 'PUT', body: { status, position } })
export const deleteTask = (id) => api(`/tasks/${id}`, { method: 'DELETE' })
