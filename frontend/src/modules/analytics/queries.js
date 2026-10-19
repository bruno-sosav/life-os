import { api } from '../../lib/api.js'
import { todayISO } from '../../lib/dates.js'

// Stats ya calculadas por el backend. weekOffset mueve la semana del Score Bruce y el radar.
export const fetchAnalyticsSummary = (weekOffset = 0) =>
  api('/analytics/summary', { params: { today: todayISO(), week_offset: weekOffset } })
