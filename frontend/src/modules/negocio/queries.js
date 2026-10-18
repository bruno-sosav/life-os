import { supabase } from '../../lib/supabase.js'
import { startOfMonth } from 'date-fns'

// ─── Proyectos ──────────────────────────────────────────────
export async function fetchProjects() {
  const { data, error } = await supabase.from('projects').select('*').order('created_at')
  if (error) throw error
  return data ?? []
}

export async function createProject(payload) {
  const { data, error } = await supabase.from('projects').insert(payload).select().single()
  if (error) throw error
  return data
}

export async function deleteProject(id) {
  const { error } = await supabase.from('projects').delete().eq('id', id)
  if (error) throw error
}

// ─── Tareas ─────────────────────────────────────────────────
export async function fetchTasks(projectId) {
  let q = supabase.from('stratus_tasks').select('*').order('created_at', { ascending: false })
  if (projectId) q = q.eq('project_id', projectId)
  const { data, error } = await q
  if (error) throw error
  return data ?? []
}

export async function createTask(payload) {
  const { data, error } = await supabase.from('stratus_tasks').insert(payload).select().single()
  if (error) throw error
  return data
}

export async function updateTask(id, patch) {
  const { data, error } = await supabase.from('stratus_tasks').update(patch).eq('id', id).select().single()
  if (error) throw error
  return data
}

export async function deleteTask(id) {
  const { error } = await supabase.from('stratus_tasks').delete().eq('id', id)
  if (error) throw error
}

// ─── Ideas ──────────────────────────────────────────────────
export async function fetchIdeas() {
  const { data, error } = await supabase.from('stratus_ideas').select('*').order('created_at', { ascending: false })
  if (error) throw error
  return data ?? []
}

export async function createIdea({ title, body, tags }) {
  const { data, error } = await supabase.from('stratus_ideas').insert({ title, body, tags }).select().single()
  if (error) throw error
  return data
}

export async function deleteIdea(id) {
  const { error } = await supabase.from('stratus_ideas').delete().eq('id', id)
  if (error) throw error
}

// ─── Objetivos ──────────────────────────────────────────────
export async function fetchGoals(month = new Date()) {
  const monthStart = startOfMonth(month).toISOString().slice(0, 10)
  const { data, error } = await supabase.from('stratus_goals').select('*').eq('month', monthStart).order('created_at')
  if (error) throw error
  return data ?? []
}

export async function createGoal({ title, month = new Date() }) {
  const monthStart = startOfMonth(month).toISOString().slice(0, 10)
  const { data, error } = await supabase.from('stratus_goals').insert({ title, month: monthStart, progress: 0 }).select().single()
  if (error) throw error
  return data
}

export async function updateGoal(id, patch) {
  const { data, error } = await supabase.from('stratus_goals').update(patch).eq('id', id).select().single()
  if (error) throw error
  return data
}

export async function deleteGoal(id) {
  const { error } = await supabase.from('stratus_goals').delete().eq('id', id)
  if (error) throw error
}
