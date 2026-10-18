import { api } from '../../lib/api.js'
import { todayISO } from '../../lib/dates.js'

// Trae los registros crudos de Stats; los cálculos (Score Bruce, radar, heatmap) siguen en index.jsx
export async function fetchAnalyticsData() {
  const d = await api('/analytics/data', { params: { today: todayISO() } })
  return {
    habits: d.habits,
    habitLogs: d.habit_logs,
    routineBlocks: d.routine_blocks,
    routineCompletions: d.routine_completions,
    gym: d.gym,
    mma: d.mma,
    weight: d.weight,
    mood: d.mood,
    nutrition: d.nutrition,
    books: d.books,
    financeIncome: d.finance_income,
    financeExpenses: d.finance_expenses,
    journalEntries: d.journal_entries,
  }
}
