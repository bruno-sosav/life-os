import { format } from 'date-fns'
import { api } from '../../../shared/lib/api.js'

// El backend acepta cualquier día del mes y filtra por el mes completo
const monthISO = (monthDate) => format(monthDate, 'yyyy-MM-dd')

// Totales, ahorro y gasto por categoría ya calculados:
// { income, expenses, savings, savings_pct, spent_pct, by_category: [{ category, total, pct }] }
export const fetchMonthSummary = (monthDate) =>
  api('/finance/summary', { params: { month: monthISO(monthDate) } })

// Categorías y fuentes en uso (son libres): { expense_categories, income_sources }
export const fetchLabels = () => api('/finance/labels')
