import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// Cada skill viene calculada: week_minutes, total_minutes, last_practice, weeks (6), resources, books
export const fetchSkills = () => api('/skills', { params: { today: todayISO() } })
export const fetchSkillTypes = () => api('/skills/types')
export const createSkill = (payload) => api('/skills', { method: 'POST', body: payload })
export const updateSkill = (id, patch) => api(`/skills/${id}`, { method: 'PATCH', body: patch })
// Borra también sus prácticas y recursos; los libros vinculados quedan
export const deleteSkill = (id) => api(`/skills/${id}`, { method: 'DELETE' })
