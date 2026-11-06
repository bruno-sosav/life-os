import { format } from 'date-fns'
import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// { days: [{ date, status, done, expected, pct }], weeks: [{ week_start, pct }], cumplido, … }
export const fetchCalendar = (month) =>
  api('/analytics/calendar', { params: { month: format(month, 'yyyy-MM-dd'), today: todayISO() } })
