import { api } from '../../../shared/lib/api.js'

export const fetchPractices = (skillId, limit = 10) =>
  api(`/skills/${skillId}/practices`, { params: { limit } })
// Con hábito vinculado, el backend lo marca cumplido ese día
export const createPractice = (payload) => api('/practices', { method: 'POST', body: payload })
export const deletePractice = (id) => api(`/practices/${id}`, { method: 'DELETE' })
