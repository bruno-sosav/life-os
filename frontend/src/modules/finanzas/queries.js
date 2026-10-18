import { api } from '../../lib/api.js'
import { format } from 'date-fns'

// El backend acepta cualquier día del mes y filtra por el mes completo
const monthISO = (monthDate) => format(monthDate, 'yyyy-MM-dd')

export const fetchMonthIncome = (monthDate) =>
  api('/finance/income', { params: { month: monthISO(monthDate) } })
export const createIncome = (payload) => api('/finance/income', { method: 'POST', body: payload })
export const deleteIncome = (id) => api(`/finance/income/${id}`, { method: 'DELETE' })

export const fetchMonthExpenses = (monthDate) =>
  api('/finance/expenses', { params: { month: monthISO(monthDate) } })
export const createExpense = (payload) => api('/finance/expenses', { method: 'POST', body: payload })
export const deleteExpense = (id) => api(`/finance/expenses/${id}`, { method: 'DELETE' })
