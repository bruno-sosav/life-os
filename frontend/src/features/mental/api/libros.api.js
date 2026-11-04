import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// { shelves: { pendiente, leyendo, leido }, year, read_this_year }
export const fetchLibrary = () => api('/books/library', { params: { today: todayISO() } })
export const createBook = (payload) => api('/books', { method: 'POST', body: payload })
export const updateBook = (id, patch) => api(`/books/${id}`, { method: 'PATCH', body: patch })
export const deleteBook = (id) => api(`/books/${id}`, { method: 'DELETE' })
