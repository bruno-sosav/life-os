import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { AXIS, GRID, INK, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

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

export default function WeightChart({ series }) {
  return (
    <Card title="Peso" subtitle="Kg · últimos 90 días">
      <div className="h-48">
        <Series data={series} dataKey="kg" name="Peso" unit=" kg" color={PICK_COLORS[0]}
          domain={['dataMin - 1', 'dataMax + 1']} empty="Registrá tu peso en Físico → Peso y nutrición" />
      </div>
    </Card>
  )
}
