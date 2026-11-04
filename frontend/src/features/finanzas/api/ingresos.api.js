import { format } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

export const fetchMonthIncome = (monthDate) =>
  api('/finance/income', { params: { month: format(monthDate, 'yyyy-MM-dd') } })
export const createIncome = (payload) => api('/finance/income', { method: 'POST', body: payload })
export const deleteIncome = (id) => api(`/finance/income/${id}`, { method: 'DELETE' })
