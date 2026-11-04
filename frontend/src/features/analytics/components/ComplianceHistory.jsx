import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip, ReferenceLine } from 'recharts'
import Card from '../../../shared/components/ui/Card.jsx'
import { fmt } from '../../../shared/lib/dates.js'
import { AXIS, GRID, INK, TOOLTIP } from './chartTheme.jsx'
import NoData from './NoData.jsx'

export default function ComplianceHistory({ history }) {
  const has = history.some((w) => w.pct != null)
  return (
    <Card title="Cumplimiento semanal" subtitle="Últimas 12 semanas · la línea marca el 70 %">
      <div className="h-52">
        {has ? (
          <ResponsiveContainer>
            <AreaChart data={history} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
              <defs>
                <linearGradient id="compliance-fill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#2EBD85" stopOpacity={0.22} />
                  <stop offset="100%" stopColor="#2EBD85" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid {...GRID} />
              <XAxis dataKey="week_start" tickFormatter={(d) => fmt(d, 'd MMM')} {...AXIS} minTickGap={16} />
              <YAxis {...AXIS} domain={[0, 100]} ticks={[0, 50, 100]} width={36} unit="%" />
              <Tooltip {...TOOLTIP} labelFormatter={(d) => `Semana del ${fmt(d, 'd MMM')}`} formatter={(v) => [`${v}%`, 'Cumplimiento']} />
              <ReferenceLine y={70} stroke={INK.axis} strokeDasharray="3 4" />
              <Area type="monotone" dataKey="pct" name="Cumplimiento" stroke="#2EBD85" strokeWidth={2} fill="url(#compliance-fill)"
                connectNulls activeDot={{ r: 5, stroke: INK.surface, strokeWidth: 2 }}
                dot={({ cx, cy, payload }) => payload.pct == null || !payload.is_current
                  ? <g key={payload.week_start} />
                  : <circle key={payload.week_start} cx={cx} cy={cy} r={5} fill="#2EBD85" stroke={INK.surface} strokeWidth={2} />}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <NoData text="Sin nada agendado en estas semanas" />
        )}
      </div>
    </Card>
  )
}
