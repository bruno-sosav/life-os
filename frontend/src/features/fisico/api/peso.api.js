import { format, subDays } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

const daysAgoISO = (n) => format(subDays(new Date(), n), 'yyyy-MM-dd')

export const fetchWeightLogs = (rangeDays = 90) =>
  api('/weight-logs', { params: { start: daysAgoISO(rangeDays) } })
export const upsertWeightLog = ({ date, weight_kg, notes }) =>
  api(`/weight-logs/${date}`, { method: 'PUT', body: { weight_kg, notes } })
export const fetchWeightGoal = () => api('/weight-goal')
export const saveWeightGoal = (weight_kg) => api('/weight-goal', { method: 'PUT', body: { weight_kg } })
