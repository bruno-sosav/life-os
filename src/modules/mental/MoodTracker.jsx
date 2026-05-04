import { useMemo, useState, useEffect } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchMoodLogs, upsertMoodLog } from './queries.js'
import { todayISO } from '../../lib/dates.js'
import { toast } from '../../store/toastStore.js'
import {
  ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend
} from 'recharts'

const MOOD_ICONS = ['😞', '😕', '😐', '🙂', '😄']
const ENERGY_ICONS = ['⚡', '⚡⚡', '⚡⚡⚡', '⚡⚡⚡⚡', '🔥']

export default function MoodTracker() {
  const moodQ = useAsync(() => fetchMoodLogs(30), [])
  const today = todayISO()
  const todayLog = (moodQ.data || []).find((m) => m.date === today)

  const [score, setScore] = useState(3)
  const [energy, setEnergy] = useState(3)
  const [sleep, setSleep] = useState(7)
  const [notes, setNotes] = useState('')

  useEffect(() => {
    if (!todayLog) return
    setScore(todayLog.mood_score || 3)
    setEnergy(todayLog.energy_score || 3)
    setSleep(todayLog.sleep_hours || 7)
    setNotes(todayLog.notes || '')
  }, [todayLog?.id])

  async function save() {
    try {
      await upsertMoodLog({ date: today, mood_score: score, energy_score: energy, sleep_hours: sleep, notes: notes || null })
      toast.success('Estado guardado ✓')
      moodQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  const avgMood = useMemo(() => {
    const last7 = (moodQ.data || []).slice(-7)
    return last7.length ? (last7.reduce((s, m) => s + (m.mood_score || 0), 0) / last7.length).toFixed(1) : '—'
  }, [moodQ.data])

  const chartData = useMemo(() =>
    (moodQ.data || []).slice(-14).map((m) => ({
      date: m.date.slice(5),
      mood: m.mood_score,
      sueño: Number(m.sleep_hours)
    })), [moodQ.data])

  return (
    <div className="space-y-4">
      <Card title="Estado de hoy" emoji="📊" subtitle={`Mood promedio 7d: ${avgMood}/5`}>
        <div className="space-y-4">
          <div>
            <label className="label">Mood</label>
            <div className="flex gap-2">
              {MOOD_ICONS.map((icon, i) => (
                <button
                  key={i}
                  onClick={() => setScore(i + 1)}
                  className={`flex-1 py-3 rounded-xl text-xl transition-all ${score === i + 1 ? 'bg-white/[0.12] scale-110' : 'opacity-35 hover:opacity-70'}`}
                >{icon}</button>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Energía</label>
            <div className="flex gap-2">
              {ENERGY_ICONS.map((icon, i) => (
                <button
                  key={i}
                  onClick={() => setEnergy(i + 1)}
                  className={`flex-1 py-2 rounded-xl text-base transition-all ${energy === i + 1 ? 'bg-white/[0.12] scale-105' : 'opacity-35 hover:opacity-70'}`}
                >{icon}</button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Sueño (h)</label>
              <input type="number" step="0.5" min={0} max={14} className="input" value={sleep} onChange={(e) => setSleep(Number(e.target.value))} />
            </div>
            <div>
              <label className="label">Notas</label>
              <input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Una línea…" />
            </div>
          </div>
          <Button className="w-full" color="purple" onClick={save}>Guardar</Button>
        </div>
      </Card>

      <Card title="Últimos 14 días" emoji="📈">
        <div className="h-48">
          {chartData.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" stroke="#ffffff22" fontSize={10} />
                <YAxis stroke="#ffffff22" fontSize={10} domain={[0, 'dataMax + 1']} />
                <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line type="monotone" dataKey="mood" stroke="#BF5AF2" strokeWidth={2.5} dot={{ r: 3 }} name="Mood" />
                <Line type="monotone" dataKey="sueño" stroke="#0A84FF" strokeWidth={2} dot={{ r: 2 }} strokeDasharray="4 3" name="Sueño" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-xs text-white/30">Sin datos suficientes</div>
          )}
        </div>
      </Card>
    </div>
  )
}
