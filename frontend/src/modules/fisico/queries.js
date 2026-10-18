import { supabase } from '../../lib/supabase.js'

// ─── Gym ────────────────────────────────────────────────────
export async function fetchGymSessions(limit = 50) {
  const { data, error } = await supabase
    .from('gym_sessions')
    .select('*, gym_exercises(*)')
    .order('date', { ascending: false })
    .limit(limit)
  if (error) throw error
  return data ?? []
}

export async function createGymSession({ date, routine_name, attended = true, notes, exercises = [] }) {
  const { data: session, error } = await supabase
    .from('gym_sessions')
    .insert({ date, routine_name, attended, notes })
    .select()
    .single()
  if (error) throw error

  if (exercises.length) {
    const rows = exercises.map((e) => ({ ...e, session_id: session.id }))
    const { error: e2 } = await supabase.from('gym_exercises').insert(rows)
    if (e2) throw e2
  }
  return session
}

export async function deleteGymSession(id) {
  const { error } = await supabase.from('gym_sessions').delete().eq('id', id)
  if (error) throw error
}

export async function fetchExerciseProgression(exerciseName) {
  const { data, error } = await supabase
    .from('gym_exercises')
    .select('exercise_name, weight_kg, reps, sets, gym_sessions!inner(date)')
    .ilike('exercise_name', exerciseName)
    .order('date', { foreignTable: 'gym_sessions', ascending: true })
  if (error) throw error
  return data ?? []
}

export async function fetchAllExerciseNames() {
  const { data, error } = await supabase
    .from('gym_exercises')
    .select('exercise_name')
  if (error) throw error
  return Array.from(new Set((data ?? []).map((d) => d.exercise_name))).sort()
}

// ─── MMA ────────────────────────────────────────────────────
export async function fetchMMASessions() {
  const { data, error } = await supabase
    .from('mma_sessions')
    .select('*')
    .order('date', { ascending: false })
  if (error) throw error
  return data ?? []
}

export async function createMMASession(payload) {
  const { data, error } = await supabase
    .from('mma_sessions')
    .insert(payload)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteMMASession(id) {
  const { error } = await supabase.from('mma_sessions').delete().eq('id', id)
  if (error) throw error
}

// ─── Peso / Nutrición ───────────────────────────────────────
export async function fetchWeightLogs(rangeDays = 90) {
  const start = new Date()
  start.setDate(start.getDate() - rangeDays)
  const { data, error } = await supabase
    .from('weight_logs')
    .select('*')
    .gte('date', start.toISOString().slice(0, 10))
    .order('date', { ascending: true })
  if (error) throw error
  return data ?? []
}

export async function upsertWeightLog({ date, weight_kg, notes }) {
  const { data, error } = await supabase
    .from('weight_logs')
    .upsert({ date, weight_kg, notes }, { onConflict: 'date' })
    .select()
    .single()
  if (error) throw error
  return data
}

export async function fetchNutritionLogs(rangeDays = 30) {
  const start = new Date()
  start.setDate(start.getDate() - rangeDays)
  const { data, error } = await supabase
    .from('nutrition_logs')
    .select('*')
    .gte('date', start.toISOString().slice(0, 10))
    .order('date', { ascending: true })
  if (error) throw error
  return data ?? []
}

export async function upsertNutritionLog(payload) {
  const { data, error } = await supabase
    .from('nutrition_logs')
    .upsert(payload, { onConflict: 'date' })
    .select()
    .single()
  if (error) throw error
  return data
}
