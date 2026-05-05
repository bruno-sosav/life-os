import { supabase } from '../../lib/supabase.js'
import { format, subDays } from 'date-fns'

// ─── Hábitos ────────────────────────────────────────────────
export async function fetchLinkedModuleHabit(module) {
  try {
    const { data, error } = await supabase
      .from('habits')
      .select('*')
      .eq('linked_module', module)
      .eq('active', true)
      .maybeSingle()
    if (error) return null
    return data
  } catch { return null }
}

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

// ─── Racha global ───────────────────────────────────────────
export async function fetchStreakRawData() {
  const start = format(subDays(new Date(), 60), 'yyyy-MM-dd')
  const [completions, habitLogs] = await Promise.all([
    supabase.from('routine_completions').select('block_id, date').gte('date', start),
    supabase.from('habit_logs').select('habit_id, date').gte('date', start).eq('completed', true)
  ])
  return { completions: completions.data || [], habitLogs: habitLogs.data || [] }
}

export function calcGlobalStreak(blocks, habits, completions, habitLogs) {
  if (!blocks && !habits) return 0
  const done = {}
  ;(completions || []).forEach(c => { done[c.date] = (done[c.date] || 0) + 1 })
  ;(habitLogs || []).forEach(l => { done[l.date] = (done[l.date] || 0) + 1 })
  let streak = 0
  const today = new Date()
  for (let i = 0; i < 60; i++) {
    const d = new Date(today); d.setDate(d.getDate() - i)
    const iso = d.toISOString().slice(0, 10)
    const dow = (d.getDay() + 6) % 7
    const expBlocks = (blocks || []).filter(b => {
      if (!b.repeat_weekly) return false
      return b.days_of_week?.length ? b.days_of_week.includes(dow) : b.day_of_week === dow
    }).length
    const expHabits = (habits || []).filter(h => !h.days_of_week?.length || h.days_of_week.includes(dow)).length
    const total = expBlocks + expHabits
    if (total === 0) continue
    const pct = (done[iso] || 0) / total
    if (i === 0 && pct < 0.7) continue // Hoy todavía no terminó, no rompe la racha
    if (pct >= 0.7) streak++
    else break
  }
  return streak
}

// ─── Cierre semanal ──────────────────────────────────────────
export function getWeekBounds(offsetWeeks = 0) {
  const today = new Date()
  const dow = (today.getDay() + 6) % 7
  const monday = new Date(today)
  monday.setDate(today.getDate() - dow - offsetWeeks * 7)
  const sunday = new Date(monday); sunday.setDate(monday.getDate() + 6)
  const fmt = (d) => d.toISOString().slice(0, 10)
  return { start: fmt(monday), end: fmt(sunday) }
}

export async function fetchWeeklyReviewStats(thisStart, thisEnd, prevStart, prevEnd) {
  const [thisLogs, prevLogs, habits, gym, mma, mood] = await Promise.all([
    supabase.from('habit_logs').select('habit_id, date, completed').gte('date', thisStart).lte('date', thisEnd),
    supabase.from('habit_logs').select('habit_id, date, completed').gte('date', prevStart).lte('date', prevEnd),
    supabase.from('habits').select('*').eq('active', true),
    supabase.from('gym_sessions').select('date, attended').gte('date', thisStart).lte('date', thisEnd),
    supabase.from('mma_sessions').select('date, attended').gte('date', thisStart).lte('date', thisEnd),
    supabase.from('mood_logs').select('mood_score, date').gte('date', thisStart).lte('date', thisEnd)
  ])
  return {
    thisLogs: thisLogs.data || [], prevLogs: prevLogs.data || [],
    habits: habits.data || [], gym: gym.data || [],
    mma: mma.data || [], mood: mood.data || []
  }
}

export async function fetchWeeklyReview(weekStart) {
  const { data } = await supabase.from('weekly_reviews').select('*').eq('week_start', weekStart).maybeSingle()
  return data
}

export async function saveWeeklyReview({ week_start, went_well, would_change }) {
  const { error } = await supabase
    .from('weekly_reviews')
    .upsert({ week_start, went_well, would_change }, { onConflict: 'week_start' })
  if (error) throw error
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
