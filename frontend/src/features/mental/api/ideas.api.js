import { api } from '../../../shared/lib/api.js'

// Sin `tag` trae todas. Las etiquetas son libres: [{ tag, count }] de las que están en uso
export const fetchMentalIdeas = (tag) => api('/ideas', { params: tag ? { tag } : {} })
export const fetchIdeaTags = () => api('/ideas/tags')
export const createMentalIdea = (payload) => api('/ideas', { method: 'POST', body: payload })
export const deleteMentalIdea = (id) => api(`/ideas/${id}`, { method: 'DELETE' })
