import { format, subDays } from 'date-fns'
import { api } from '../../../lib/api.js'
import { todayISO } from '../../../lib/dates.js'

const daysAgoISO = (n) => format(subDays(new Date(), n), 'yyyy-MM-dd')

export const fetchNutritionLogs = (rangeDays = 30) =>
  api('/nutrition-logs', { params: { start: daysAgoISO(rangeDays) } })
export const upsertNutritionLog = ({ date, ...payload }) =>
  api(`/nutrition-logs/${date}`, { method: 'PUT', body: payload })
// { avg_quality } de los últimos 7 días, o null sin registros
export const fetchNutritionAverage = () =>
  api('/nutrition-logs/average', { params: { today: todayISO() } })
