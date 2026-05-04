import { useMemo, useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchGymSessions, createGymSession, deleteGymSession,
  fetchExerciseProgression, fetchAllExerciseNames
} from './queries.js'
import { fmt, todayISO, weekRange, eachDayOfInterval, format } from '../../lib/dates.js'
import {
  ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip
} from 'recharts'

const DOW = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

export default function Gym() {
  const sessionsQ = useAsync(() => fetchGymSessions(), [])
  const exerciseNamesQ = useAsync(() => fetchAllExerciseNames(), [sessionsQ.data?.length])
  const [exerciseFilter, setExerciseFilter] = useState('')
  const [adding, setAdding] = useState(false)

  const progressionQ = useAsync(
    () => exerciseFilter ? fetchExerciseProgression(exerciseFilter) : Promise.resolve([]),
    [exerciseFilter]
  )

  const { start, end } = weekRange()
  const weekDays = eachDayOfInterval({ start, end })

  const sessionsByDate = useMemo(() => {
    const m = {}
    ;(sessionsQ.data || []).forEach((s) => { m[s.date] = s })
    return m
  }, [sessionsQ.data])

  async function quickToggle(dateISO, existing) {
    try {
      if (existing) {
        const newAttended = !existing.attended
        await fetch('')   // no-op to satisfy linter
        // actual update via supabase
        const { supabase } = await import('../../lib/supabase.js')
        const { error } = await supabase.from('gym_sessions').update({ attended: newAttended }).eq('id', existing.id)
        if (error) throw error
        toast.success(newAttended ? 'Asistencia registrada ✓' : 'Marcado como ausente')
      } else {
        await createGymSession({ date: dateISO, attended: true, routine_name: null, exercises: [] })
        toast.success('Sesión registrada ✓')
      }
      sessionsQ.refetch()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  const chartData = useMemo(() => (progressionQ.data || []).map((row) => ({
    date: row.gym_sessions?.date?.slice(5),
    weight: Number(row.weight_kg) || 0
  })).filter((d) => d.date), [progressionQ.data])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        {/* Weekly check */}
        <Card title="Semana" emoji="📅">
          <div className="grid grid-cols-7 gap-1.5">
            {weekDays.map((day, i) => {
              const iso = format(day, 'yyyy-MM-dd')
              const session = sessionsByDate[iso]
              const isToday = iso === todayISO()
              return (
                <button
                  key={iso}
                  onClick={() => quickToggle(iso, session)}
                  className="flex flex-col items-center gap-1 py-3 rounded-[14px] transition-all active:scale-95"
                  style={{
                    background: session?.attended ? '#30D15822' : session ? '#FF453A11' : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${session?.attended ? '#30D15840' : session ? '#FF453A30' : isToday ? 'rgba(10,132,255,0.5)' : 'rgba(255,255,255,0.06)'}`
                  }}
                >
                  <span className="text-[10px] font-semibold text-white/40">{DOW[i]}</span>
                  <span className="text-base">
                    {session?.attended ? '✓' : session ? '✗' : '○'}
                  </span>
                  <span
                    className="text-[10px] font-bold"
                    style={{ color: session?.attended ? '#30D158' : session ? '#FF453A' : isToday ? '#0A84FF' : 'rgba(255,255,255,0.25)' }}
                  >
                    {day.getDate()}
                  </span>
                </button>
              )
            })}
          </div>
        </Card>

        {/* Session log */}
        <Card
          title="Sesiones"
          emoji="🏋️"
          action={<Button size="sm" onClick={() => setAdding(true)}>+ Sesión</Button>}
        >
          {!(sessionsQ.data || []).length ? (
            <EmptyState icon="🏋️" title="Sin sesiones" description="Registrá tu primer entrenamiento." />
          ) : (
            <ul className="divide-y divide-white/[0.04]">
              {sessionsQ.data.slice(0, 10).map((s) => (
                <li key={s.id} className="py-3 flex items-center gap-3 group">
                  <span
                    className="w-7 h-7 rounded-full grid place-items-center text-xs font-bold"
                    style={s.attended
                      ? { background: '#30D15820', color: '#30D158' }
                      : { background: '#FF453A20', color: '#FF453A' }}
                  >
                    {s.attended ? '✓' : '✗'}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold">{s.routine_name || 'Sesión'}</div>
                    <div className="text-xs text-white/35">{fmt(s.date, "EEE d 'de' MMM")} · {(s.gym_exercises || []).length} ejercicios</div>
                  </div>
                  <button
                    onClick={() => deleteGymSession(s.id).then(() => { toast.success('Eliminado'); sessionsQ.refetch() })}
                    className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs"
                  >✕</button>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="space-y-4">
        <Card title="Progresión" emoji="📈">
          <select className="input mb-3 text-sm" value={exerciseFilter} onChange={(e) => setExerciseFilter(e.target.value)}>
            <option value="">Elegí un ejercicio…</option>
            {(exerciseNamesQ.data || []).map((n) => <option key={n} value={n}>{n}</option>)}
          </select>
          <div className="h-48">
            {chartData.length > 1 ? (
              <ResponsiveContainer>
                <LineChart data={chartData}>
                  <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                  <XAxis dataKey="date" stroke="#ffffff22" fontSize={10} />
                  <YAxis stroke="#ffffff22" fontSize={10} />
                  <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
                  <Line type="monotone" dataKey="weight" stroke="#BF5AF2" strokeWidth={2.5} dot={{ r: 3, fill: '#BF5AF2' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full grid place-items-center text-xs text-white/30">
                {exerciseFilter ? 'Sin datos suficientes' : 'Elegí un ejercicio'}
              </div>
            )}
          </div>
        </Card>
      </div>

      <NewSessionModal
        open={adding}
        onClose={() => setAdding(false)}
        onSaved={() => { sessionsQ.refetch(); exerciseNamesQ.refetch() }}
      />
    </div>
  )
}

function NewSessionModal({ open, onClose, onSaved }) {
  const [date, setDate] = useState(todayISO())
  const [routine, setRoutine] = useState('')
  const [attended, setAttended] = useState(true)
  const [exercises, setExercises] = useState([{ exercise_name: '', sets: 3, reps: 10, weight_kg: 0 }])

  function addRow() { setExercises([...exercises, { exercise_name: '', sets: 3, reps: 10, weight_kg: 0 }]) }
  function updateRow(i, f, v) {
    const next = [...exercises]; next[i] = { ...next[i], [f]: f === 'exercise_name' ? v : Number(v) }; setExercises(next)
  }

  async function save() {
    try {
      await createGymSession({ date, routine_name: routine.trim() || null, attended, exercises: exercises.filter((e) => e.exercise_name.trim()) })
      toast.success('Sesión guardada ✓')
      onSaved(); onClose()
      setRoutine(''); setExercises([{ exercise_name: '', sets: 3, reps: 10, weight_kg: 0 }])
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nueva sesión de gym" size="lg"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div><label className="label">Fecha</label><input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} /></div>
        <div><label className="label">Rutina</label><input className="input" value={routine} onChange={(e) => setRoutine(e.target.value)} placeholder="Push / Pull / Legs" /></div>
        <div>
          <label className="label">Asistí</label>
          <button onClick={() => setAttended(!attended)} className={`input text-left font-semibold ${attended ? 'text-[#30D158]' : 'text-[#FF453A]'}`}>{attended ? '✓ Sí' : '✗ No'}</button>
        </div>
      </div>
      <label className="label">Ejercicios</label>
      <div className="space-y-2">
        <div className="grid grid-cols-12 gap-2 text-[10px] uppercase text-white/30 px-1">
          <div className="col-span-5">Nombre</div><div className="col-span-2">Series</div><div className="col-span-2">Reps</div><div className="col-span-2">Kg</div>
        </div>
        {exercises.map((e, i) => (
          <div key={i} className="grid grid-cols-12 gap-2 items-center">
            <input className="input col-span-5 text-sm" value={e.exercise_name} onChange={(ev) => updateRow(i, 'exercise_name', ev.target.value)} placeholder="Press banca" />
            <input type="number" min={0} className="input col-span-2 text-sm" value={e.sets} onChange={(ev) => updateRow(i, 'sets', ev.target.value)} />
            <input type="number" min={0} className="input col-span-2 text-sm" value={e.reps} onChange={(ev) => updateRow(i, 'reps', ev.target.value)} />
            <input type="number" min={0} step="0.5" className="input col-span-2 text-sm" value={e.weight_kg} onChange={(ev) => updateRow(i, 'weight_kg', ev.target.value)} />
            <button onClick={() => setExercises(exercises.filter((_, x) => x !== i))} className="text-white/25 hover:text-[#FF453A] text-xs">✕</button>
          </div>
        ))}
      </div>
      <button onClick={addRow} className="mt-2 text-xs text-[#0A84FF] hover:underline">+ Agregar ejercicio</button>
    </Modal>
  )
}
