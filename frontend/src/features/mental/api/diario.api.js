import { api } from '../../../shared/lib/api.js'

export const fetchJournalEntries = () => api('/journal-entries')
export const createJournalEntry = (payload) => api('/journal-entries', { method: 'POST', body: payload })
export const deleteJournalEntry = (id) => api(`/journal-entries/${id}`, { method: 'DELETE' })
