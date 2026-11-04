import { api } from '../../../lib/api.js'

export const saveWeeklyReview = ({ week_start, went_well, would_change }) =>
  api(`/weekly-reviews/${week_start}`, { method: 'PUT', body: { went_well, would_change } })
