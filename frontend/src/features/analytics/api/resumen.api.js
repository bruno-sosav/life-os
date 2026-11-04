import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// Stats ya calculadas por el backend. weekOffset mueve la semana del cumplimiento y el radar.
export const fetchAnalyticsSummary = (weekOffset = 0) =>
  api('/analytics/summary', { params: { today: todayISO(), week_offset: weekOffset } })
