import { useState } from 'react'
import { addMonths, format } from 'date-fns'
import PageHeader from '../../../shared/components/ui/PageHeader.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fmt } from '../../../shared/lib/dates.js'
import { fetchMonthExpenses } from '../api/gastos.api.js'
import { fetchMonthIncome } from '../api/ingresos.api.js'
import { fetchLabels, fetchMonthSummary } from '../api/resumen.api.js'
import MonthSummary from '../components/MonthSummary.jsx'
import CategoryBreakdown from '../components/CategoryBreakdown.jsx'
import IncomeList from '../components/IncomeList.jsx'
import ExpenseTable from '../components/ExpenseTable.jsx'
import IncomeModal from '../components/IncomeModal.jsx'
import ExpenseModal from '../components/ExpenseModal.jsx'

const EMPTY_SUMMARY = { income: 0, expenses: 0, savings: 0, savings_pct: null, spent_pct: null, by_category: [] }
const capitalize = (s) => s.replace(/^\w/, (c) => c.toUpperCase())

export default function FinanzasPage() {
  const [refDate, setRefDate] = useState(new Date())
  const [adding, setAdding] = useState(null) // null | 'ingreso' | 'gasto'
  const [highlight, setHighlight] = useState(null) // la fila recién cargada, para el destello

  const monthKey = format(refDate, 'yyyy-MM')
  const summaryQ = useAsync(() => fetchMonthSummary(refDate), [monthKey])
  const incomeQ = useAsync(() => fetchMonthIncome(refDate), [monthKey])
  const expensesQ = useAsync(() => fetchMonthExpenses(refDate), [monthKey])
  const labelsQ = useAsync(() => fetchLabels(), [])

  // Todos los totales vienen calculados del backend
  const summary = summaryQ.data || EMPTY_SUMMARY
  const labels = labelsQ.data || { expense_categories: [], income_sources: [] }

  function refetch() { summaryQ.refetch(); incomeQ.refetch(); expensesQ.refetch(); labelsQ.refetch() }

  function onSaved(created) {
    setHighlight(created.id)
    refetch()
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Finanzas"
        subtitle="Ingresos, gastos y ahorro"
        actions={
          <div className="flex items-center gap-1 rounded-xl bg-ink-900 border border-ink-700 p-1">
            <button onClick={() => setRefDate(addMonths(refDate, -1))} aria-label="Mes anterior"
              className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">‹</button>
            <span className="px-2 text-sm font-semibold min-w-[8.5rem] text-center">{capitalize(fmt(refDate, 'MMMM yyyy'))}</span>
            <button onClick={() => setRefDate(addMonths(refDate, 1))} aria-label="Mes siguiente"
              className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">›</button>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <MonthSummary summary={summary} />
        <CategoryBreakdown categories={summary.by_category} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
        <div className="lg:col-span-3">
          <ExpenseTable expenses={expensesQ.data || []} highlight={highlight} onAdd={() => setAdding('gasto')} onChanged={refetch} />
        </div>
        <div className="lg:col-span-2">
          <IncomeList income={incomeQ.data || []} highlight={highlight} onAdd={() => setAdding('ingreso')} onChanged={refetch} />
        </div>
      </div>

      <IncomeModal open={adding === 'ingreso'} onClose={() => setAdding(null)} refDate={refDate} onSaved={onSaved} sources={labels.income_sources} />
      <ExpenseModal open={adding === 'gasto'} onClose={() => setAdding(null)} onSaved={onSaved} categories={labels.expense_categories} left={summary.savings} />
    </div>
  )
}
