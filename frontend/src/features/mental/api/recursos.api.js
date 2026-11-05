import { api } from '../../../shared/lib/api.js'

export const createResource = (skillId, payload) =>
  api(`/skills/${skillId}/resources`, { method: 'POST', body: payload })
export const deleteResource = (id) => api(`/skill-resources/${id}`, { method: 'DELETE' })
