import { supabase } from '../../lib/supabase.js'
import { format, subDays, subMonths, startOfMonth } from 'date-fns'

export async function fetchAnalyticsData() {
  const start90 = format(subDays(new Date(), 90), 'yyyy-MM-dd')
  const start30 = format(subDays(new Date(), 30), 'yyyy-MM-dd')
  const start6m = format(startOfMonth(subMonths(new Date(), 5)), 'yyyy-MM-dd')

  const results = await Promise.allSettled([
    supabase.from('habits').select('*').eq('active', true),
    supabase.from('habit_logs').select('*').gte('date', start90),
    supabase.from('routine_blocks').select('*'),
    supabase.from('routine_completions').select('block_id, date').gte('date', start90),
    supabase.from('gym_sessions').select('date, attended').gte('date', start90),
    supabase.from('mma_sessions').select('date, attended').gte('date', start90),
    supabase.from('weight_logs').select('date, weight_kg').order('date', { ascending: true }),
    supabase.from('mood_logs').select('date, mood_score, sleep_hours').gte('date', start30),
    supabase.from('nutrition_logs').select('date').gte('date', start90),
    supabase.from('books').select('status, finished_at'),
    supabase.from('finance_income').select('month, amount').gte('month', start6m),
    supabase.from('finance_expenses').select('date, amount').gte('date', start6m),
    supabase.from('journal_entries').select('created_at').gte('created_at', start90),
  ])

  const safe = (r) => (r.status === 'fulfilled' ? r.value.data || [] : [])
  const [
    habits, habitLogs, routineBlocks, routineCompletions,
    gym, mma, weight, mood, nutrition, books,
    financeIncome, financeExpenses, journalEntries,
  ] = results.map(safe)

  return {
    habits, habitLogs, routineBlocks, routineCompletions,
    gym, mma, weight, mood, nutrition, books,
    financeIncome, financeExpenses, journalEntries,
  }
}
