import { format } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

export const fetchMonthExpenses = (monthDate) =>
  api('/finance/expenses', { params: { month: format(monthDate, 'yyyy-MM-dd') } })
export const createExpense = (payload) => api('/finance/expenses', { method: 'POST', body: payload })
export const deleteExpense = (id) => api(`/finance/expenses/${id}`, { method: 'DELETE' })
