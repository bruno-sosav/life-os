import { useMemo, useState, useEffect } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchMoodLogs, upsertMoodLog } from './queries.js'
import { todayISO } from '../../lib/dates.js'
import { MOOD_ICONS } from '../../lib/constants.js'
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts'

export default function MoodPanel() {
  const moodQ = useAsync(() => fetchMoodLogs(30), [])
  const today = todayISO()
  const todayMood = (moodQ.data || []).find((m) => m.date === today)

  const [score, setScore] = useState(3)
  const [sleep, setSleep] = useState(7)
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (todayMood) {
      setScore(todayMood.mood_score || 3)
      setSleep(todayMood.sleep_hours || 7)
      setNotes(todayMood.notes || '')
    }
  }, [todayMood?.id])

  async function save() {
    await upsertMoodLog({
      date: today,
      mood_score: score,
      sleep_hours: sleep,
      notes: notes || null
    })
    moodQ.refetch()
  }

  const chartData = useMemo(() => {
    return (moodQ.data || []).slice(-14).map((m) => ({
      date: m.date.slice(5),
      mood: m.mood_score
    }))
  }, [moodQ.data])

  return (
    <Card title="Estado de hoy" subtitle="Mood y sueño">
      <div>
        <label className="label">¿Cómo estás?</label>
        <div className="flex gap-2 justify-between mb-3">
          {MOOD_ICONS.map((icon, i) => (
            <button
              key={i}
              onClick={() => setScore(i + 1)}
              className={`text-2xl transition w-12 h-12 rounded-lg ${
                score === i + 1 ? 'bg-purple-brand/20 ring-1 ring-purple-brand' : 'opacity-50 hover:opacity-100'
              }`}
            >
              {icon}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label className="label">Horas de sueño</label>
            <input type="number" step="0.5" min={0} max={14} className="input" value={sleep} onChange={(e) => setSleep(Number(e.target.value))} />
          </div>
          <div>
            <label className="label">Score</label>
            <div className="input bg-ink-800/60 text-purple-brand font-semibold">{score} / 5</div>
          </div>
        </div>
        <div className="mb-3">
          <label className="label">Nota</label>
          <textarea className="input min-h-[70px]" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Una línea sobre el día…" />
        </div>
        <Button className="w-full" onClick={save}>Guardar</Button>
      </div>

      <div className="mt-5">
        <div className="text-xs uppercase tracking-wider text-ink-400 font-semibold mb-2">Mood últimos 14d</div>
        <div className="h-32">
          {chartData.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" stroke="#5b5b68" fontSize={10} />
                <YAxis stroke="#5b5b68" fontSize={10} domain={[0, 5]} />
                <Tooltip contentStyle={{ background: '#1d1d22', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }} />
                <Line type="monotone" dataKey="mood" stroke="#1D9E75" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-xs text-ink-400">Sin datos suficientes</div>
          )}
        </div>
      </div>
    </Card>
  )
}
