import { format, subDays } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

// El mood y el sueño se cargan en Hoy; el backend es el de Mental
export const fetchMoodLogs = (days = 1) =>
  api('/mood-logs', { params: { start: format(subDays(new Date(), days), 'yyyy-MM-dd') } })
export const upsertMoodLog = ({ date, ...payload }) =>
  api(`/mood-logs/${date}`, { method: 'PUT', body: payload })
