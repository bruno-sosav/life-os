import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// El detalle de un día es la agenda del dashboard: qué tocaba y qué se hizo
export const fetchDay = (dateISO) =>
  api('/dashboard/agenda', { params: { date: dateISO, today: todayISO() } })
