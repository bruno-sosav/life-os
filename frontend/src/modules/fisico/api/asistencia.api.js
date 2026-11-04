import { format } from 'date-fns'
import { api } from '../../../lib/api.js'
import { todayISO } from '../../../lib/dates.js'

// { count, days: [{ date, activity_ids }] }: qué tipos entrenaste cada día
export const fetchTrainingWeek = () => api('/training/week', { params: { today: todayISO() } })
export const fetchTrainingMonth = (month) =>
  api('/training/month', { params: { month: format(month, 'yyyy-MM-dd') } })
