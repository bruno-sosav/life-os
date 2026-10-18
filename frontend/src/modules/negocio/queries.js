import { api } from '../../lib/api.js'
import { format } from 'date-fns'

// ─── Proyectos ──────────────────────────────────────────────
export const fetchProjects = () => api('/projects')
export const createProject = (payload) => api('/projects', { method: 'POST', body: payload })
export const deleteProject = (id) => api(`/projects/${id}`, { method: 'DELETE' })

// ─── Tareas ─────────────────────────────────────────────────
// completed_at lo maneja el backend según el status
export const fetchTasks = (projectId) => api('/tasks', { params: { project_id: projectId } })
export const createTask = (payload) => api('/tasks', { method: 'POST', body: payload })
export const updateTask = (id, patch) => api(`/tasks/${id}`, { method: 'PATCH', body: patch })
export const deleteTask = (id) => api(`/tasks/${id}`, { method: 'DELETE' })

// ─── Ideas ──────────────────────────────────────────────────
export const fetchIdeas = () => api('/business-ideas')
export const createIdea = ({ title, body, tags }) =>
  api('/business-ideas', { method: 'POST', body: { title, body, tags } })
export const deleteIdea = (id) => api(`/business-ideas/${id}`, { method: 'DELETE' })

// ─── Objetivos ──────────────────────────────────────────────
// El backend normaliza `month` al día 1 del mes
const monthISO = (month) => format(month, 'yyyy-MM-dd')

export const fetchGoals = (month = new Date()) => api('/goals', { params: { month: monthISO(month) } })
export const createGoal = ({ title, month = new Date() }) =>
  api('/goals', { method: 'POST', body: { title, month: monthISO(month) } })
export const updateGoal = (id, patch) => api(`/goals/${id}`, { method: 'PATCH', body: patch })
export const deleteGoal = (id) => api(`/goals/${id}`, { method: 'DELETE' })
