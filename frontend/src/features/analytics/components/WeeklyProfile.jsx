import { ResponsiveContainer, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Tooltip, Legend } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { INK, LEGEND, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

// Esta semana en color; la anterior en gris punteado, como referencia
export default function WeeklyProfile({ radar }) {
  const has = radar.some((r) => r.semana > 0 || r.anterior > 0)
  return (
    <Card title="Perfil semanal" subtitle="Hábitos, entrenos y mental · esta semana vs la anterior">
      <div className="h-56">
        {has ? (
          <ResponsiveContainer>
            <RadarChart data={radar} outerRadius="70%">
              <PolarGrid stroke={INK.grid} />
              <PolarAngleAxis dataKey="axis" tick={{ fill: INK.axis, fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
              <Radar dataKey="anterior" name="Semana anterior" stroke={INK.axis} fill="none" strokeWidth={2} strokeDasharray="4 3" />
              <Radar dataKey="semana" name="Esta semana" stroke={PICK_COLORS[0]} fill={PICK_COLORS[0]} fillOpacity={0.18} strokeWidth={2}
                dot={{ r: 4, fill: PICK_COLORS[0], stroke: INK.surface, strokeWidth: 2 }} />
              <Legend {...LEGEND} />
              <Tooltip {...TOOLTIP} formatter={(v, n) => [`${v}%`, n]} />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <NoData text="Sin datos suficientes todavía" />
        )}
      </div>
    </Card>
  )
}
