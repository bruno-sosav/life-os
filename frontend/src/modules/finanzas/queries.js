import { supabase } from '../../lib/supabase.js'
import { format, startOfMonth, endOfMonth } from 'date-fns'

export async function fetchMonthIncome(monthDate) {
  const month = format(startOfMonth(monthDate), 'yyyy-MM-dd')
  const { data, error } = await supabase
    .from('finance_income')
    .select('*')
    .eq('month', month)
    .order('created_at')
  if (error) throw error
  return data ?? []
}

export async function createIncome(payload) {
  const { data, error } = await supabase
    .from('finance_income')
    .insert(payload)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteIncome(id) {
  const { error } = await supabase.from('finance_income').delete().eq('id', id)
  if (error) throw error
}

export async function fetchMonthExpenses(monthDate) {
  const start = format(startOfMonth(monthDate), 'yyyy-MM-dd')
  const end = format(endOfMonth(monthDate), 'yyyy-MM-dd')
  const { data, error } = await supabase
    .from('finance_expenses')
    .select('*')
    .gte('date', start)
    .lte('date', end)
    .order('date', { ascending: false })
  if (error) throw error
  return data ?? []
}

export async function createExpense(payload) {
  const { data, error } = await supabase
    .from('finance_expenses')
    .insert(payload)
    .select()
    .single()
  if (error) throw error
  return data
}

export async function deleteExpense(id) {
  const { error } = await supabase.from('finance_expenses').delete().eq('id', id)
  if (error) throw error
}
