import { api } from '../../../shared/lib/api.js'

// Cada lista trae sus ítems en orden: pendientes primero, después los hechos
export const fetchLists = () => api('/lists')
export const createList = (payload) => api('/lists', { method: 'POST', body: payload })
export const updateList = (id, patch) => api(`/lists/${id}`, { method: 'PATCH', body: patch })
export const deleteList = (id) => api(`/lists/${id}`, { method: 'DELETE' })

export const addItem = (listId, payload) => api(`/lists/${listId}/items`, { method: 'POST', body: payload })
export const updateItem = (id, patch) => api(`/list-items/${id}`, { method: 'PATCH', body: patch })
export const moveItem = (id, position) => api(`/list-items/${id}/move`, { method: 'PUT', body: { position } })
export const deleteItem = (id) => api(`/list-items/${id}`, { method: 'DELETE' })
export const clearDone = (listId) => api(`/lists/${listId}/done`, { method: 'DELETE' })
// "Practicar →": el ítem pasa a ser una skill. Devuelve { skill_id }
export const itemToSkill = (id) => api(`/list-items/${id}/skill`, { method: 'POST' })
