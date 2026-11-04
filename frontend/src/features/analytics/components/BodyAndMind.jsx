import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { AXIS, GRID, INK, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

// Una serie por gráfico: el mood (1 a 5) y el sueño (horas) no comparten eje
function Series({ data, dataKey, name, unit, color, domain, empty }) {
  if (data.length < 2) return <NoData text={empty} />
  return (
    <ResponsiveContainer>
      <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid {...GRID} />
        <XAxis dataKey="date" tickFormatter={(d) => fmt(d, 'd MMM')} {...AXIS} minTickGap={20} />
        <YAxis {...AXIS} domain={domain} width={36} />
        <Tooltip {...TOOLTIP} labelFormatter={(d) => fmt(d, "d 'de' MMM")} formatter={(v) => [`${v}${unit}`, name]} />
        <Line type="monotone" dataKey={dataKey} name={name} stroke={color} strokeWidth={2} connectNulls
          dot={false} activeDot={{ r: 5, stroke: INK.surface, strokeWidth: 2 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function WeightChart({ series }) {
  return (
    <Card title="Peso" subtitle="Kg · últimos 90 días">
      <div className="h-48">
        <Series data={series} dataKey="kg" name="Peso" unit=" kg" color={PICK_COLORS[0]}
          domain={['dataMin - 1', 'dataMax + 1']} empty="Registrá tu peso en Físico → Peso y nutrición" />
      </div>
    </Card>
  )
}

export function MoodSleep({ series }) {
  return (
    <Card title="Mood y sueño" subtitle="Últimos 30 días">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <div className="label">Mood (1 a 5)</div>
          <div className="h-40">
            <Series data={series} dataKey="mood" name="Mood" unit="" color={PICK_COLORS[4]} domain={[1, 5]} empty="Registrá tu estado en Mental" />
          </div>
        </div>
        <div>
          <div className="label">Sueño (horas)</div>
          <div className="h-40">
            <Series data={series} dataKey="sleep" name="Sueño" unit=" h" color={PICK_COLORS[5]} domain={[0, 'dataMax + 1']} empty="Registrá tu sueño en Mental" />
          </div>
        </div>
      </div>
    </Card>
  )
}
