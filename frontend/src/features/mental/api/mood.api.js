import { format, subDays } from 'date-fns'
import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

export const fetchMoodLogs = (days = 30) =>
  api('/mood-logs', { params: { start: format(subDays(new Date(), days), 'yyyy-MM-dd') } })
// { avg_mood } de los últimos 7 días, o null sin registros
export const fetchMoodAverage = () => api('/mood-logs/average', { params: { today: todayISO() } })
export const upsertMoodLog = ({ date, ...payload }) =>
  api(`/mood-logs/${date}`, { method: 'PUT', body: payload })
