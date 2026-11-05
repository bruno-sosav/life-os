import Card from '../../../shared/components/ui/Card.jsx'
import { money } from '../lib/dinero.js'

// El ahorro grande, ingresos contra gastos y la barra partida. Todo viene calculado del backend.
export default function MonthSummary({ summary }) {
  const { income, expenses, savings, savings_pct: savingsPct, spent_pct: spentPct } = summary
  return (
    <Card>
      <div className="flex items-baseline justify-between mb-1">
        <span className="text-[11px] text-ink-400 font-medium">Ahorro del mes</span>
        {savingsPct != null && <span className="font-mono text-xs text-ink-400">{savingsPct}% del ingreso</span>}
      </div>
      <div className={`font-mono text-3xl sm:text-4xl font-bold tracking-tight ${savings >= 0 ? 'text-up' : 'text-down'}`}>
        {money(savings)}
      </div>
      <div className="grid grid-cols-2 gap-3 mt-4">
        <div>
          <div className="text-[11px] text-ink-400">Ingresos</div>
          <div className="font-mono text-lg font-bold text-up">{money(income)}</div>
        </div>
        <div className="text-right">
          <div className="text-[11px] text-ink-400">Gastos</div>
          <div className="font-mono text-lg font-bold text-down">{money(expenses)}</div>
        </div>
      </div>
      {income > 0 || expenses > 0 ? (
        <>
          <div className="flex gap-[3px] h-1.5 mt-3" aria-hidden="true">
            <div className="bg-up rounded-sm transition-all duration-500" style={{ flex: Math.max(savings, 0) }} />
            <div className="bg-down rounded-sm transition-all duration-500" style={{ flex: expenses }} />
          </div>
          <p className="text-xs text-ink-400 mt-2">
            {spentPct != null
              ? <>Gastaste el <span className="font-mono text-ink-100">{spentPct}%</span> de lo que entró</>
              : 'Este mes no cargaste ingresos'}
          </p>
        </>
      ) : (
        <p className="text-xs text-ink-400 mt-3">Sin movimientos este mes</p>
      )}
    </Card>
  )
}
