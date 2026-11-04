import { useState } from 'react'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, ReferenceDot } from 'recharts'
import Card from '../../../components/Card.jsx'
import { useAsync } from '../../../hooks/useAsync.js'
import { fmt } from '../../../lib/dates.js'
import { fetchExerciseNames, fetchExerciseProgression, fetchFieldSeries } from '../api/sesiones.api.js'
import { CHARTABLE } from '../campos.js'

// La carga máxima de un ejercicio (de cualquier tipo) o un campo de número/escala de un tipo
export default function ProgressChart({ activities, version }) {
  const namesQ = useAsync(() => fetchExerciseNames(), [version])
  const fields = activities.flatMap((a) => a.fields.filter((f) => CHARTABLE.includes(f.type)).map((f) => ({ activity: a, field: f })))
  const [choice, setChoice] = useState('')
  const [kind, ...rest] = choice.split(':')
  const key = rest.join(':')

  const seriesQ = useAsync(async () => {
    if (kind === 'ejercicio') return fetchExerciseProgression(key)
    if (kind === 'campo') {
      const [activityId, fieldId] = key.split('|')
      return { points: await fetchFieldSeries(activityId, fieldId), best: null }
    }
    return { points: [], best: null }
  }, [choice, version])

  const names = namesQ.data || []
  if (!names.length && !fields.length) return null
  const points = seriesQ.data?.points || []
  const best = seriesQ.data?.best
  const data = points.map((p) => ({ date: p.date, label: fmt(p.date, 'd MMM'), value: p.value }))

  return (
    <Card title="Progresión" subtitle={best ? <>Récord <span className="font-mono text-up">{best.value} kg</span> el <span className="font-mono">{fmt(best.date, 'd MMM')}</span></> : null}>
      <select className="input mb-3 text-sm" value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="Qué graficar">
        <option value="">Elegí un ejercicio…</option>
        {names.map((n) => <option key={n} value={`ejercicio:${n}`}>{n} (kg máx.)</option>)}
        {fields.map(({ activity, field }) => (
          <option key={field.id} value={`campo:${activity.id}|${field.id}`}>
            {activity.name} · {field.name}{field.unit ? ` (${field.unit})` : ''}
          </option>
        ))}
      </select>
      <div className="h-48">
        {data.length > 1 ? (
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid stroke="#1A201E" vertical={false} />
              <XAxis dataKey="label" stroke="#8C948F" fontSize={10} tickLine={false} />
              <YAxis stroke="#8C948F" fontSize={10} tickLine={false} width={32} domain={['dataMin - 2', 'dataMax + 2']} />
              <Tooltip contentStyle={{ background: '#0F1312', border: '1px solid #1F2623', borderRadius: 8 }} labelStyle={{ color: '#8C948F' }} />
              <Line type="monotone" dataKey="value" stroke="#2EBD85" strokeWidth={2.5} dot={{ r: 3, fill: '#2EBD85' }} isAnimationActive />
              {best && <ReferenceDot x={fmt(best.date, 'd MMM')} y={best.value} r={6} fill="#2EBD85" stroke="#07090A" strokeWidth={2} />}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full grid place-items-center text-xs text-ink-400">
            {choice ? 'Hacen falta al menos 2 registros' : 'Elegí qué ver'}
          </div>
        )}
      </div>
    </Card>
  )
}
