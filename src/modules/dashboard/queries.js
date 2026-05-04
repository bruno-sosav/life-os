import { supabase } from '../../lib/supabase.js'
import { format, subDays } from 'date-fns'

// ─── Hábitos ────────────────────────────────────────────────
export async function fetchActiveHabits() {
  const { data, error } = await supabase
    .from('habits')
    .select('*')
    .eq('active', true)
    .order('start_time', { ascending: true, nullsFirst: false })
    .order('sort_order')
    .order('created_at')
  if (error) throw error
  return data ?? []
}

export async function createHabit(payload) {
  const { data, error } = await supabase
    .from('habits')
    .insert({ active: true, ...payload })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function updateHabit(id, patch) {
  const { data, error } = await supabase
    .from('habits')
    .update(patch)
    .eq('id', id)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteHabit(id) {
  const { error } = await supabase.from('habits').delete().eq('id', id)
  if (error) throw error
}

export async function fetchHabitLogsRange(startISO, endISO) {
  const { data, error } = await supabase
    .from('habit_logs')
    .select('*')
    .gte('date', startISO)
    .lte('date', endISO)
  if (error) throw error
  return data ?? []
}

export async function toggleHabitLog({ habit_id, date, completed }) {
  const { data, error } = await supabase
    .from('habit_logs')
    .upsert({ habit_id, date, completed }, { onConflict: 'habit_id,date' })
    .select()
    .single()
  if (error) throw error
  return data
}

// ─── Routine blocks ──────────────────────────────────────────
export async function fetchRoutineBlocks() {
  const { data, error } = await supabase
    .from('routine_blocks')
    .select('*')
    .order('hour_start')
  if (error) throw error
  return data ?? []
}

export async function upsertRoutineBlock(payload) {
  const { data, error } = await supabase
    .from('routine_blocks')
    .upsert(payload)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteRoutineBlock(id) {
  const { error } = await supabase.from('routine_blocks').delete().eq('id', id)
  if (error) throw error
}

// ─── Routine completions ────────────────────────────────────
export async function fetchRoutineCompletions(dateISO) {
  const { data, error } = await supabase
    .from('routine_completions')
    .select('*')
    .eq('date', dateISO)
  if (error) throw error
  return data ?? []
}

export async function toggleRoutineCompletion({ block_id, date, completed }) {
  if (!completed) {
    // eliminar si existe
    const { error } = await supabase
      .from('routine_completions')
      .delete()
      .eq('block_id', block_id)
      .eq('date', date)
    if (error) throw error
  } else {
    const { error } = await supabase
      .from('routine_completions')
      .upsert({ block_id, date, completed: true }, { onConflict: 'block_id,date' })
    if (error) throw error
  }
}
