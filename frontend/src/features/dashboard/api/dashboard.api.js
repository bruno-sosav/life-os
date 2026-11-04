import { api } from '../../../shared/lib/api.js'
import { todayISO } from '../../../shared/lib/dates.js'

// La agenda llega armada: secciones, estado de cada ítem y progreso del día
export const fetchAgenda = (dateISO) =>
  api('/dashboard/agenda', { params: { date: dateISO, today: todayISO() } })

export async function fetchGlobalStreak() {
  const { streak } = await api('/dashboard/streak', { params: { today: todayISO() } })
  return streak
}

// Estadísticas de la semana más la revisión guardada
export const fetchWeeklyReview = () =>
  api('/dashboard/weekly-review', { params: { today: todayISO() } })
