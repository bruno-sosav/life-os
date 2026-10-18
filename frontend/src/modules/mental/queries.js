import { api } from '../../lib/api.js'
import { format, subDays } from 'date-fns'

// ─── Libros ────────────────────────────────────────────────
export const fetchBooks = () => api('/books')
export const createBook = (payload) => api('/books', { method: 'POST', body: payload })
export const updateBook = (id, patch) => api(`/books/${id}`, { method: 'PATCH', body: patch })
export const deleteBook = (id) => api(`/books/${id}`, { method: 'DELETE' })

// ─── Mood ──────────────────────────────────────────────────
export const fetchMoodLogs = (days = 30) =>
  api('/mood-logs', { params: { start: format(subDays(new Date(), days), 'yyyy-MM-dd') } })

export const upsertMoodLog = ({ date, ...payload }) =>
  api(`/mood-logs/${date}`, { method: 'PUT', body: payload })

// ─── Diario ────────────────────────────────────────────────
export const fetchJournalEntries = () => api('/journal-entries')
export const createJournalEntry = (payload) => api('/journal-entries', { method: 'POST', body: payload })
export const deleteJournalEntry = (id) => api(`/journal-entries/${id}`, { method: 'DELETE' })

// ─── Ideas mentales ────────────────────────────────────────
export const fetchMentalIdeas = () => api('/ideas')
export const createMentalIdea = (payload) => api('/ideas', { method: 'POST', body: payload })
export const deleteMentalIdea = (id) => api(`/ideas/${id}`, { method: 'DELETE' })
