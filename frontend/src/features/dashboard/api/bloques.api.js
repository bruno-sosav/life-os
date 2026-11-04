import { api } from '../../../shared/lib/api.js'

export function upsertRoutineBlock({ id, ...payload }) {
  return id
    ? api(`/routine-blocks/${id}`, { method: 'PUT', body: payload })
    : api('/routine-blocks', { method: 'POST', body: payload })
}
export const deleteRoutineBlock = (id) => api(`/routine-blocks/${id}`, { method: 'DELETE' })
export const fetchBlockCategories = () => api('/routine-blocks/categories')
export const toggleRoutineCompletion = ({ block_id, date, completed }) =>
  api('/routine-completions', { method: 'PUT', body: { block_id, date, completed } })
