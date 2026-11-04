import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import Card from '../../../components/Card.jsx'
import { fmt } from '../../../lib/dates.js'
import { AXIS, GRID, LEGEND, TOOLTIP } from './chartTheme.jsx'

const money = (n) => `$${Math.round(n).toLocaleString('es-AR')}`
const compact = (n) => (n >= 1e6 ? `${Math.round(n / 1e5) / 10}M` : n >= 1e3 ? `${Math.round(n / 1e3)}k` : String(n))

// Ingresos (verde) contra gastos (rojo) por mes, y el % de ahorro de los últimos 3
export default function FinanceChart({ months }) {
  if (!months.some((m) => m.income > 0 || m.expenses > 0)) return null
  return (
    <Card title="Finanzas" subtitle="Ingresos y gastos · últimos 6 meses">
      <div className="h-52">
        <ResponsiveContainer>
          <BarChart data={months} barCategoryGap="30%" barGap={2} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
            <CartesianGrid {...GRID} />
            <XAxis dataKey="month" tickFormatter={(m) => fmt(m, 'MMM')} {...AXIS} />
            <YAxis {...AXIS} tickFormatter={compact} width={44} />
            <Tooltip {...TOOLTIP} labelFormatter={(m) => fmt(m, 'MMMM yyyy')} formatter={(v, n) => [money(v), n]} />
            <Legend {...LEGEND} />
            <Bar dataKey="income" name="Ingresos" fill="#2EBD85" radius={[4, 4, 0, 0]} />
            <Bar dataKey="expenses" name="Gastos" fill="#F6465D" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-ink-700">
        {months.slice(-3).map((m) => (
          <div key={m.month} className="text-center">
            <div className="text-[11px] text-ink-400 capitalize">{fmt(m.month, 'MMMM')}</div>
            <div className={`font-mono text-xl font-bold ${m.savings_pct == null ? 'text-ink-400' : m.savings_pct >= 0 ? 'text-up' : 'text-down'}`}>
              {m.savings_pct != null ? `${m.savings_pct}%` : '—'}
            </div>
            <div className="text-[10px] text-ink-400 uppercase tracking-wider">ahorro</div>
          </div>
        ))}
      </div>
    </Card>
  )
}
