import { api } from '../lib/api.js'

// Para elegir un hábito vinculado (Físico, Mental): registrar ahí lo marca en Hoy
export const fetchActiveHabits = () => api('/habits', { params: { active: true } })
