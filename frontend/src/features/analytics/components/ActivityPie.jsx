import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { INK, LEGEND, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

// Cada tipo con su color propio (el que tiene en Físico); el total va en el centro
export default function ActivityPie({ distribution }) {
  const data = distribution.map((a) => ({ name: a.name, value: a.count, color: a.color || INK.axis }))
  const total = data.reduce((sum, d) => sum + d.value, 0)
  return (
    <Card title="Entrenamientos" subtitle="Por tipo · últimos 30 días">
      <div className="h-56 relative">
        {data.length ? (
          <>
            <ResponsiveContainer>
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="45%" innerRadius={52} outerRadius={78}
                  stroke={INK.surface} strokeWidth={2} paddingAngle={1} animationDuration={600}>
                  {data.map((d) => <Cell key={d.name} fill={d.color} />)}
                </Pie>
                <Tooltip {...TOOLTIP} formatter={(v, n) => [`${v} días`, n]} />
                <Legend {...LEGEND} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute left-0 right-0 top-[45%] -translate-y-1/2 text-center pointer-events-none">
              <div className="font-mono text-2xl font-bold">{total}</div>
              <div className="text-[10px] text-ink-400 uppercase tracking-wider">días</div>
            </div>
          </>
        ) : (
          <NoData text="Sin entrenamientos en los últimos 30 días" />
        )}
      </div>
    </Card>
  )
}
