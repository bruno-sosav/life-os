import { api } from '../../../lib/api.js'

export const fetchIdeas = () => api('/business-ideas')
export const createIdea = ({ title, body, tags }) =>
  api('/business-ideas', { method: 'POST', body: { title, body, tags } })
export const deleteIdea = (id) => api(`/business-ideas/${id}`, { method: 'DELETE' })
