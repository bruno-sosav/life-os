import Button from '../../../shared/components/ui/Button.jsx'
import Card from '../../../shared/components/ui/Card.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { colorFor } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { deleteExpense } from '../api/gastos.api.js'
import { money } from '../lib/dinero.js'

const COLUMNS = 'grid grid-cols-[52px_minmax(0,1fr)_auto_32px] gap-3 items-center'

// Los gastos del mes como tabla: fecha, qué fue (con su categoría) y monto
export default function ExpenseTable({ expenses, highlight, onAdd, onChanged }) {
  async function remove(expense) {
    if (!confirm(`¿Borrar el gasto de ${money(expense.amount)}?`)) return
    try {
      await deleteExpense(expense.id)
      toast.success('Gasto borrado')
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Card title="Gastos" action={<Button size="sm" onClick={onAdd}>+ Gasto</Button>}>
      {!expenses.length ? (
        <EmptyState icon="—" title="Sin gastos" description="Registrá tus gastos del mes." />
      ) : (
        <div role="table" aria-label="Gastos del mes">
          <div role="row" className={`${COLUMNS} px-2 pb-2 text-[10px] font-semibold tracking-wider uppercase text-ink-400`}>
            <span role="columnheader">Fecha</span>
            <span role="columnheader">Gasto</span>
            <span role="columnheader" className="text-right">Monto</span>
            <span />
          </div>
          {expenses.map((e) => (
            <div role="row" key={e.id}
              className={`${COLUMNS} px-2 py-2.5 rounded-lg border-t border-ink-700 ${e.id === highlight ? 'flash-new' : ''}`}>
              <span role="cell" className="font-mono text-xs text-ink-400">{fmt(e.date, 'dd/MM')}</span>
              <span role="cell" className="min-w-0">
                <span className="block text-sm truncate">{e.description || e.category}</span>
                <span className="block text-[10px] font-bold tracking-wider uppercase truncate" style={{ color: colorFor(e.category) }}>{e.category}</span>
              </span>
              <span role="cell" className="font-mono text-sm font-semibold text-right">{money(e.amount)}</span>
              <button onClick={() => remove(e)} aria-label={`Borrar gasto de ${money(e.amount)}`}
                className="w-8 h-8 rounded-lg grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs">✕</button>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
