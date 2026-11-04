import { ResponsiveContainer, BarChart, Bar, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { AXIS, GRID, INK, LEGEND, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

const SHOWN = 5 // más hábitos que colores no se inventan: el resto va junto en "Otros"

// Cada hábito conserva su color por orden; con más de 5, los demás se suman en "Otros"
function series(habits, weeks) {
  const shown = habits.slice(0, SHOWN).map((h, i) => ({ key: h.id, name: h.name, color: PICK_COLORS[i] }))
  const rest = habits.slice(SHOWN)
  if (!rest.length) return { bars: shown, data: weeks }
  const data = weeks.map((w) => ({ ...w, otros: rest.reduce((sum, h) => sum + (w[h.id] || 0), 0) }))
  return { bars: [...shown, { key: 'otros', name: 'Otros', color: INK.axis }], data }
}

export default function HabitsByWeek({ habitsByWeek }) {
  const { bars, data } = series(habitsByWeek.habits, habitsByWeek.weeks)
  return (
    <Card title="Hábitos por semana" subtitle="Días cumplidos · últimas 8 semanas">
      <div className="h-56">
        {bars.length ? (
          <ResponsiveContainer>
            <BarChart data={data} barCategoryGap="35%" margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <CartesianGrid {...GRID} />
              <XAxis dataKey="week_start" tickFormatter={(d) => fmt(d, 'd MMM')} {...AXIS} minTickGap={12} />
              <YAxis {...AXIS} allowDecimals={false} width={36} />
              <Tooltip {...TOOLTIP} labelFormatter={(d) => `Semana del ${fmt(d, 'd MMM')}`} />
              <Legend {...LEGEND} />
              {bars.map((b, i) => (
                // 2 px del color de fondo entre segmentos; solo el de arriba lleva las puntas redondeadas
                <Bar key={b.key} dataKey={b.key} name={b.name} stackId="habitos" fill={b.color}
                  stroke={INK.surface} strokeWidth={2} radius={i === bars.length - 1 ? [4, 4, 0, 0] : 0} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <NoData text="Sin hábitos activos todavía" />
        )}
      </div>
    </Card>
  )
}
