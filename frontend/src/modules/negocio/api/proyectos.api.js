import { api } from '../../../lib/api.js'

export const fetchProjects = () => api('/projects')
export const createProject = (payload) => api('/projects', { method: 'POST', body: payload })
export const updateProject = (id, patch) => api(`/projects/${id}`, { method: 'PATCH', body: patch })
// Borra el proyecto con todas sus tareas
export const deleteProject = (id) => api(`/projects/${id}`, { method: 'DELETE' })
