import { api } from '../../lib/api.js'
import { format, subDays } from 'date-fns'
import { todayISO } from '../../lib/dates.js'

// ─── Libros ────────────────────────────────────────────────
// { shelves: { pendiente, leyendo, leido }, year, read_this_year }
export const fetchLibrary = () => api('/books/library', { params: { today: todayISO() } })
export const createBook = (payload) => api('/books', { method: 'POST', body: payload })
export const updateBook = (id, patch) => api(`/books/${id}`, { method: 'PATCH', body: patch })
export const deleteBook = (id) => api(`/books/${id}`, { method: 'DELETE' })

// ─── Mood ──────────────────────────────────────────────────
export const fetchMoodLogs = (days = 30) =>
  api('/mood-logs', { params: { start: format(subDays(new Date(), days), 'yyyy-MM-dd') } })

// { avg_mood } de los últimos 7 días, o null sin registros
export const fetchMoodAverage = () => api('/mood-logs/average', { params: { today: todayISO() } })

export const upsertMoodLog = ({ date, ...payload }) =>
  api(`/mood-logs/${date}`, { method: 'PUT', body: payload })

// ─── Diario ────────────────────────────────────────────────
export const fetchJournalEntries = () => api('/journal-entries')
export const createJournalEntry = (payload) => api('/journal-entries', { method: 'POST', body: payload })
export const deleteJournalEntry = (id) => api(`/journal-entries/${id}`, { method: 'DELETE' })

// ─── Ideas mentales ────────────────────────────────────────
// Sin `tag` trae todas. Las etiquetas son libres: [{ tag, count }] de las que están en uso
export const fetchMentalIdeas = (tag) => api('/ideas', { params: tag ? { tag } : {} })
export const fetchIdeaTags = () => api('/ideas/tags')
export const createMentalIdea = (payload) => api('/ideas', { method: 'POST', body: payload })
export const deleteMentalIdea = (id) => api(`/ideas/${id}`, { method: 'DELETE' })
