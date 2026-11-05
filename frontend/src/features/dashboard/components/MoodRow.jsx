import { useEffect, useState } from 'react'
import Card from '../../../shared/components/ui/Card.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { todayISO } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { fetchMoodLogs, upsertMoodLog } from '../api/mood.api.js'

const MOODS = ['Mal', 'Flojo', 'Normal', 'Bien', 'Muy bien']

// Cómo estás y cuánto dormiste: un toque y queda guardado (cuenta en el cierre semanal)
export default function MoodRow() {
  const today = todayISO()
  const logsQ = useAsync(() => fetchMoodLogs(1), [])
  const saved = (logsQ.data || []).find((m) => m.date === today)
  const [mood, setMood] = useState(null)
  const [sleep, setSleep] = useState(null)

  useEffect(() => {
    if (!saved) return
    setMood(saved.mood_score ?? null)
    setSleep(saved.sleep_hours != null ? Number(saved.sleep_hours) : null)
  }, [saved?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  async function save(patch) {
    const next = { mood_score: mood, sleep_hours: sleep, ...patch }
    if ('mood_score' in patch) setMood(patch.mood_score)
    if ('sleep_hours' in patch) setSleep(patch.sleep_hours)
    try {
      await upsertMoodLog({ date: today, energy_score: saved?.energy_score ?? null, notes: saved?.notes ?? null, ...next })
    } catch (e) { toast.error('No se pudo guardar: ' + e.message) }
  }

  const changeSleep = (delta) => save({ sleep_hours: Math.min(14, Math.max(0, (sleep ?? 7) + delta)) })

  return (
    <Card className="mb-4">
      <div className="flex flex-col sm:flex-row sm:items-center gap-4">
        <div className="flex-1">
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-[11px] text-ink-400 font-medium" id="mood-label">Cómo estás hoy</span>
            <span className="text-xs text-ink-300">{mood ? MOODS[mood - 1] : '—'}</span>
          </div>
          <div className="grid grid-cols-5 gap-1.5" role="group" aria-labelledby="mood-label">
            {MOODS.map((label, i) => {
              const value = i + 1
              const on = mood === value
              return (
                <button key={value} onClick={() => save({ mood_score: on ? null : value })} aria-pressed={on} aria-label={label}
                  className={`h-10 rounded-lg border font-mono text-sm font-bold transition-colors ${
                    on ? 'bg-accent border-accent text-ink-100' : 'border-ink-600 text-ink-400 hover:text-ink-100'
                  }`}>{value}</button>
              )
            })}
          </div>
        </div>
        <div className="sm:w-44">
          <div className="text-[11px] text-ink-400 font-medium mb-2" id="sleep-label">Dormiste</div>
          <div className="flex items-center gap-1.5" role="group" aria-labelledby="sleep-label">
            <button onClick={() => changeSleep(-0.5)} aria-label="Media hora menos"
              className="w-10 h-10 rounded-lg border border-ink-600 text-ink-300 hover:text-ink-100">−</button>
            <span className="flex-1 text-center font-mono text-lg font-bold">{sleep != null ? `${sleep} h` : '—'}</span>
            <button onClick={() => changeSleep(0.5)} aria-label="Media hora más"
              className="w-10 h-10 rounded-lg border border-ink-600 text-ink-300 hover:text-ink-100">+</button>
          </div>
        </div>
      </div>
    </Card>
  )
}
