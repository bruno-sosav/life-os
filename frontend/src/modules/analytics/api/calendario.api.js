import { format } from 'date-fns'
import { api } from '../../../lib/api.js'
import { todayISO } from '../../../lib/dates.js'

// { days: [{ date, status, done, expected, pct }], weeks: [{ week_start, pct }], cumplido, … }
export const fetchCalendar = (month) =>
  api('/analytics/calendar', { params: { month: format(month, 'yyyy-MM-dd'), today: todayISO() } })

// El detalle de un día es la agenda del dashboard: qué tocaba y qué se hizo
export const fetchDay = (dateISO) =>
  api('/dashboard/agenda', { params: { date: dateISO, today: todayISO() } })
