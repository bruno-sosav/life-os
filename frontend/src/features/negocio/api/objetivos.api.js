import { format } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

// El backend normaliza `month` al día 1 del mes
const monthISO = (month) => format(month, 'yyyy-MM-dd')

export const fetchGoals = (month = new Date()) => api('/goals', { params: { month: monthISO(month) } })
export const createGoal = ({ title, month = new Date() }) =>
  api('/goals', { method: 'POST', body: { title, month: monthISO(month) } })
export const updateGoal = (id, patch) => api(`/goals/${id}`, { method: 'PATCH', body: patch })
export const deleteGoal = (id) => api(`/goals/${id}`, { method: 'DELETE' })
