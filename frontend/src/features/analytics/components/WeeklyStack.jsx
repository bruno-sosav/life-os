import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { AXIS, GRID, INK, LEGEND, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

const SHOWN = 5 // más series que colores no se inventan: el resto va junto en "Otros"

// Cada serie conserva su color por orden; con más de 5, las demás se suman en "Otros"
function series(items, weeks) {
  const shown = items.slice(0, SHOWN).map((it, i) => ({ key: it.id, name: it.name, color: PICK_COLORS[i] }))
  const rest = items.slice(SHOWN)
  if (!rest.length) return { bars: shown, data: weeks }
  const data = weeks.map((w) => ({ ...w, otros: rest.reduce((sum, it) => sum + (w[it.id] || 0), 0) }))
  return { bars: [...shown, { key: 'otros', name: 'Otros', color: INK.axis }], data }
}

// Barras apiladas por semana: hábitos cumplidos, minutos de práctica por skill…
// `items`: [{ id, name }]; `weeks`: [{ week_start, <id>: valor }]
export default function WeeklyStack({ title, subtitle, items, weeks, unit = '', empty }) {
  const { bars, data } = series(items, weeks)
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="h-56">
        {bars.length ? (
          <ResponsiveContainer>
            <BarChart data={data} barCategoryGap="35%" margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid {...GRID} />
              <XAxis dataKey="week_start" tickFormatter={(d) => fmt(d, 'd MMM')} {...AXIS} minTickGap={12} />
              <YAxis {...AXIS} allowDecimals={false} width={36} />
              <Tooltip {...TOOLTIP} labelFormatter={(d) => `Semana del ${fmt(d, 'd MMM')}`} formatter={(v, n) => [`${v}${unit}`, n]} />
              <Legend {...LEGEND} />
              {bars.map((b, i) => (
                // 2 px del color de fondo entre segmentos; solo el de arriba lleva las puntas redondeadas
                <Bar key={b.key} dataKey={b.key} name={b.name} stackId="semana" fill={b.color}
                  stroke={INK.surface} strokeWidth={2} radius={i === bars.length - 1 ? [4, 4, 0, 0] : 0} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <NoData text={empty} />
        )}
      </div>
    </Card>
  )
}
