import Button from '../../../shared/components/ui/Button.jsx'
import Card from '../../../shared/components/ui/Card.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { deleteIncome } from '../api/ingresos.api.js'
import { money } from '../lib/dinero.js'

export default function IncomeList({ income, highlight, onAdd, onChanged }) {
  async function remove(entry) {
    if (!confirm(`¿Borrar el ingreso de ${money(entry.amount)}?`)) return
    try {
      await deleteIncome(entry.id)
      toast.success('Ingreso borrado')
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Card title="Ingresos" action={<Button size="sm" onClick={onAdd}>+ Ingreso</Button>}>
      {!income.length ? (
        <EmptyState icon="—" title="Sin ingresos" description="Anotá lo que entra este mes." />
      ) : (
        <ul className="divide-y divide-ink-700">
          {income.map((entry) => (
            <li key={entry.id} className={`py-2.5 px-1 -mx-1 rounded-lg flex items-center gap-3 ${entry.id === highlight ? 'flash-new' : ''}`}>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">{entry.source || 'Ingreso'}</div>
                {entry.notes && <div className="text-xs text-ink-400 truncate">{entry.notes}</div>}
              </div>
              <span className="font-mono text-sm font-semibold text-up">{money(entry.amount)}</span>
              <button onClick={() => remove(entry)} aria-label={`Borrar ingreso de ${money(entry.amount)}`}
                className="w-8 h-8 rounded-lg grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs">✕</button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
