import { api } from '../../lib/api.js'
import { format } from 'date-fns'

// El backend acepta cualquier día del mes y filtra por el mes completo
const monthISO = (monthDate) => format(monthDate, 'yyyy-MM-dd')

// Totales, ahorro y gasto por categoría ya calculados:
// { income, expenses, savings, savings_pct, spent_pct, by_category: [{ category, total, pct }] }
export const fetchMonthSummary = (monthDate) =>
  api('/finance/summary', { params: { month: monthISO(monthDate) } })

// Categorías y fuentes en uso (son libres): { expense_categories, income_sources }
export const fetchLabels = () => api('/finance/labels')

export const fetchMonthIncome = (monthDate) =>
  api('/finance/income', { params: { month: monthISO(monthDate) } })
export const createIncome = (payload) => api('/finance/income', { method: 'POST', body: payload })
export const deleteIncome = (id) => api(`/finance/income/${id}`, { method: 'DELETE' })

export const fetchMonthExpenses = (monthDate) =>
  api('/finance/expenses', { params: { month: monthISO(monthDate) } })
export const createExpense = (payload) => api('/finance/expenses', { method: 'POST', body: payload })
export const deleteExpense = (id) => api(`/finance/expenses/${id}`, { method: 'DELETE' })
