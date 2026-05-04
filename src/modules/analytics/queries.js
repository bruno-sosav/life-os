import { supabase } from '../../lib/supabase.js'
import { format, subDays } from 'date-fns'

export async function fetchAnalyticsData() {
  const start60 = format(subDays(new Date(), 60), 'yyyy-MM-dd')
  const start30 = format(subDays(new Date(), 30), 'yyyy-MM-dd')

  const [habits, habitLogs, gym, mma, weight, mood, nutrition, tasks, books] = await Promise.all([
    supabase.from('habits').select('*').eq('active', true),
    supabase.from('habit_logs').select('*').gte('date', start60),
    supabase.from('gym_sessions').select('date, attended').gte('date', start60),
    supabase.from('mma_sessions').select('date, attended').gte('date', start60),
    supabase.from('weight_logs').select('*').order('date', { ascending: true }),
    supabase.from('mood_logs').select('*').gte('date', start30),
    supabase.from('nutrition_logs').select('*').gte('date', start30),
    supabase.from('stratus_tasks').select('status, completed_at, created_at'),
    supabase.from('books').select('status, finished_at')
  ])

  return {
    habits: habits.data || [],
    habitLogs: habitLogs.data || [],
    gym: gym.data || [],
    mma: mma.data || [],
    weight: weight.data || [],
    mood: mood.data || [],
    nutrition: nutrition.data || [],
    tasks: tasks.data || [],
    books: books.data || []
  }
}
