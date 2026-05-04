import { supabase } from '../../lib/supabase.js'
import { format, subDays } from 'date-fns'

// ─── Libros ────────────────────────────────────────────────
export async function fetchBooks() {
  const { data, error } = await supabase.from('books').select('*').order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}
export async function createBook(payload) {
  const { data, error } = await supabase.from('books').insert(payload).select().single()
  if (error) throw error
  return data
}
export async function updateBook(id, patch) {
  const { data, error } = await supabase.from('books').update(patch).eq('id', id).select().single()
  if (error) throw error
  return data
}
export async function deleteBook(id) {
  const { error } = await supabase.from('books').delete().eq('id', id)
  if (error) throw error
}

// ─── Mood ──────────────────────────────────────────────────
export async function fetchMoodLogs(days = 30) {
  const start = format(subDays(new Date(), days), 'yyyy-MM-dd')
  const { data, error } = await supabase.from('mood_logs').select('*').gte('date', start).order('date')
  if (error) throw error
  return data ?? []
}
export async function upsertMoodLog(payload) {
  const { data, error } = await supabase.from('mood_logs').upsert(payload, { onConflict: 'date' }).select().single()
  if (error) throw error
  return data
}

// ─── Diario ────────────────────────────────────────────────
export async function fetchJournalEntries() {
  const { data, error } = await supabase.from('journal_entries').select('*').order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}
export async function createJournalEntry(payload) {
  const { data, error } = await supabase.from('journal_entries').insert(payload).select().single()
  if (error) throw error
  return data
}
export async function deleteJournalEntry(id) {
  const { error } = await supabase.from('journal_entries').delete().eq('id', id)
  if (error) throw error
}

// ─── Ideas mentales ────────────────────────────────────────
export async function fetchMentalIdeas() {
  const { data, error } = await supabase.from('ideas').select('*').order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}
export async function createMentalIdea(payload) {
  const { data, error } = await supabase.from('ideas').insert(payload).select().single()
  if (error) throw error
  return data
}
export async function deleteMentalIdea(id) {
  const { error } = await supabase.from('ideas').delete().eq('id', id)
  if (error) throw error
}
