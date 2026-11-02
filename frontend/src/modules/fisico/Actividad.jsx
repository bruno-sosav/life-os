import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchSessions, createSession, deleteSession, fetchAttendanceWeek, toggleAttendance,
  fetchActivityMonth, fetchExerciseNames, fetchExerciseProgression, fetchFieldSeries
} from './queries.js'
import { CHARTABLE, formatValue, hasExercises } from './campos.js'
import { fmt, todayISO, format, parseISO } from '../../lib/dates.js'
import {
  ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip
} from 'recharts'

const DOW = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

export default function Actividad({ activity }) {
  const color = activity.color || '#0A84FF'
  const sessionsQ = useAsync(() => fetchSessions(activity.id), [activity.id])
  const weekQ = useAsync(() => fetchAttendanceWeek(activity.id), [activity.id])
  const [refDate, setRefDate] = useState(new Date())
  const monthISO = format(refDate, 'yyyy-MM-01')
  const monthQ = useAsync(() => fetchActivityMonth(activity.id, monthISO), [activity.id, monthISO])
  const [adding, setAdding] = useState(false)
  const habit = weekQ.data?.habit

  function refreshSessions() {
    sessionsQ.refetch()
    monthQ.refetch()
    weekQ.refetch()
  }

  async function quickToggle(dateISO) {
    try {
      const { attended } = await toggleAttendance(activity.id, dateISO)
      toast.success(attended ? `¡${activity.name} completado! ✓` : 'Desmarcado')
      if (habit) weekQ.refetch()
      else refreshSessions()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  function moveMonth(delta) {
    const d = new Date(refDate)
    d.setMonth(d.getMonth() + delta)
    setRefDate(d)
  }

  const monthDays = monthQ.data?.days || []

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        <Card
          title="Esta semana"
          subtitle={habit ? `Sincronizado con hábito "${habit.name}"` : 'Sin hábito vinculado: se marca en las sesiones'}
        >
          <div className="grid grid-cols-7 gap-1.5">
            {(weekQ.data?.days || []).map(({ date: iso, attended }, i) => {
              const isToday = iso === todayISO()
              return (
                <button
                  key={iso}
                  onClick={() => quickToggle(iso)}
                  className="flex flex-col items-center gap-1 py-3 rounded-[14px] transition-all active:scale-95"
                  style={{
                    background: attended ? '#30D15822' : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${attended ? '#30D15840' : isToday ? 'rgba(10,132,255,0.5)' : 'rgba(255,255,255,0.06)'}`
                  }}
                >
                  <span className="text-[10px] font-semibold text-white/40">{DOW[i]}</span>
                  <span className="text-base">{attended ? '✓' : '○'}</span>
                  <span className="text-[10px] font-bold" style={{ color: attended ? '#30D158' : isToday ? '#0A84FF' : 'rgba(255,255,255,0.25)' }}>{fmt(iso, 'd')}</span>
                </button>
              )
            })}
          </div>
        </Card>

        <Card
          title="Sesiones"
          action={<Button size="sm" onClick={() => setAdding(true)} style={{ backgroundColor: color }}>+ Sesión</Button>}
        >
          {!(sessionsQ.data || []).length ? (
            <EmptyState icon={activity.emoji || '✨'} title="Sin sesiones" description="Registrá tu primera sesión." />
          ) : (
            <ul className="divide-y divide-white/[0.04]">
              {sessionsQ.data.slice(0, 15).map((s) => (
                <SessionRow key={s.id} session={s} activity={activity} onDeleted={refreshSessions} />
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="space-y-4">
        <Card
          title={fmt(refDate, 'MMMM yyyy').replace(/^\w/, (c) => c.toUpperCase())}
          subtitle={`${monthQ.data?.count ?? 0} sesiones este mes`}
          action={
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={() => moveMonth(-1)} aria-label="Mes anterior">◀</Button>
              <Button variant="ghost" size="sm" onClick={() => moveMonth(1)} aria-label="Mes siguiente">▶</Button>
            </div>
          }
        >
          <div className="grid grid-cols-7 gap-1">
            {['L', 'M', 'M', 'J', 'V', 'S', 'D'].map((d, i) => <div key={i} className="text-[10px] text-center text-white/30 uppercase py-1">{d}</div>)}
            {monthDays.length > 0 && Array.from({ length: (parseISO(monthDays[0].date).getDay() + 6) % 7 }).map((_, i) => <div key={`o${i}`} />)}
            {monthDays.map(({ date: iso, attended }) => {
              const hasSession = attended !== null
              const isToday = iso === todayISO()
              return (
                <button
                  key={iso}
                  onClick={() => quickToggle(iso)}
                  className="aspect-square rounded-xl text-[11px] grid place-items-center transition"
                  style={{
                    background: attended ? '#30D15820' : hasSession ? '#FF453A15' : isToday ? '#0A84FF15' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${isToday ? '#0A84FF50' : 'transparent'}`,
                    color: attended ? '#30D158' : hasSession ? '#FF453A' : isToday ? '#0A84FF' : 'rgba(255,255,255,0.5)',
                    fontWeight: (hasSession || isToday) ? 700 : 400
                  }}
                >
                  {fmt(iso, 'd')}
                </button>
              )
            })}
          </div>
        </Card>

        <ProgressChart activity={activity} color={color} version={sessionsQ.data?.length} />
      </div>

      <NewSessionModal
        open={adding}
        activity={activity}
        onClose={() => setAdding(false)}
        onSaved={refreshSessions}
      />
    </div>
  )
}

function SessionRow({ session, activity, onDeleted }) {
  // Incluye los campos archivados: el historial se sigue leyendo
  const details = activity.fields
    .filter((f) => session.values[f.id] !== undefined)
    .map((f) => `${f.name}: ${formatValue(f, session.values[f.id])}`)
  if (session.exercises.length) details.push(`${session.exercises.length} ejercicios`)

  async function remove() {
    if (!confirm('¿Eliminar esta sesión?')) return
    await deleteSession(session.id)
    toast.success('Eliminado')
    onDeleted()
  }

  return (
    <li className="py-3 flex items-center gap-3 group">
      <span
        className="w-7 h-7 rounded-full grid place-items-center text-xs font-bold shrink-0"
        style={session.attended
          ? { background: '#30D15820', color: '#30D158' }
          : { background: '#FF453A20', color: '#FF453A' }}
      >
        {session.attended ? '✓' : '✗'}
      </span>
      <div className="flex-1 min-w-0">
        <div className="text-sm font-semibold">{fmt(session.date, "EEE d 'de' MMM")}</div>
        {details.length > 0 && <div className="text-xs text-white/40 truncate">{details.join(' · ')}</div>}
        {session.notes && <div className="text-xs text-white/30 truncate">{session.notes}</div>}
      </div>
      <button onClick={remove} aria-label="Eliminar sesión"
        className="opacity-0 group-hover:opacity-100 focus:opacity-100 text-white/25 hover:text-[#FF453A] text-xs">✕</button>
    </li>
  )
}

// Gráfico de cualquier campo de número o escala, o de la carga máxima de un ejercicio
function ProgressChart({ activity, color, version }) {
  const fields = activity.fields.filter((f) => CHARTABLE.includes(f.type))
  const namesQ = useAsync(
    () => hasExercises(activity) ? fetchExerciseNames(activity.id) : Promise.resolve([]),
    [activity.id, version]
  )
  const [choice, setChoice] = useState('')
  const [kind, key] = choice.split(':')
  const seriesQ = useAsync(() => {
    if (kind === 'campo') return fetchFieldSeries(activity.id, key)
    if (kind === 'ejercicio') return fetchExerciseProgression(activity.id, key)
    return Promise.resolve([])
  }, [activity.id, choice, version])

  const exerciseNames = namesQ.data || []
  if (!fields.length && !exerciseNames.length) return null
  const data = (seriesQ.data || []).map((p) => ({ date: p.date.slice(5), value: p.value }))

  return (
    <Card title="Progresión">
      <select className="input mb-3 text-sm" value={choice} onChange={(e) => setChoice(e.target.value)} aria-label="Qué graficar">
        <option value="">Elegí qué ver…</option>
        {fields.map((f) => (
          <option key={f.id} value={`campo:${f.id}`}>{f.name}{f.unit ? ` (${f.unit})` : ''}{f.archived ? ' · archivado' : ''}</option>
        ))}
        {exerciseNames.map((n) => <option key={n} value={`ejercicio:${n}`}>🏋️ {n} (kg máx.)</option>)}
      </select>
      <div className="h-48">
        {data.length > 1 ? (
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="date" stroke="#ffffff22" fontSize={10} />
              <YAxis stroke="#ffffff22" fontSize={10} />
              <Tooltip contentStyle={{ background: '#18181f', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 12 }} />
              <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2.5} dot={{ r: 3, fill: color }} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-full grid place-items-center text-xs text-white/30">
            {choice ? 'Hacen falta al menos 2 registros' : 'Elegí un campo o ejercicio'}
          </div>
        )}
      </div>
    </Card>
  )
}

const emptyExercise = () => ({ exercise_name: '', sets: 3, reps: 10, weight_kg: '' })

function NewSessionModal({ open, activity, onClose, onSaved }) {
  const fields = activity.fields.filter((f) => !f.archived && f.type !== 'ejercicios')
  const withExercises = hasExercises(activity)
  const [date, setDate] = useState(todayISO())
  const [values, setValues] = useState({})
  const [notes, setNotes] = useState('')
  const [exercises, setExercises] = useState([emptyExercise()])

  function reset() {
    setValues({}); setNotes(''); setExercises([emptyExercise()])
  }

  function updateExercise(i, key, value) {
    setExercises(exercises.map((e, x) => (x === i ? { ...e, [key]: value } : e)))
  }

  async function save() {
    try {
      await createSession({
        activity_id: activity.id,
        date,
        attended: true,
        notes: notes.trim() || null,
        values,
        exercises: withExercises
          ? exercises
            .filter((e) => e.exercise_name.trim())
            .map((e) => ({
              exercise_name: e.exercise_name.trim(),
              sets: e.sets === '' ? null : Number(e.sets),
              reps: e.reps === '' ? null : Number(e.reps),
              weight_kg: e.weight_kg === '' ? null : Number(e.weight_kg)
            }))
          : []
      })
      toast.success('Sesión guardada ✓')
      reset(); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title={`Nueva sesión · ${activity.name}`} size={withExercises ? 'lg' : 'md'}
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div>
          <label className="label" htmlFor="session-date">Fecha</label>
          <input id="session-date" type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>

        {fields.map((f) => (
          <FieldInput
            key={f.id}
            field={f}
            value={values[f.id]}
            onChange={(v) => setValues({ ...values, [f.id]: v })}
          />
        ))}

        {withExercises && (
          <div>
            <span className="label">Ejercicios</span>
            <div className="space-y-2">
              <div className="grid grid-cols-12 gap-2 text-[10px] uppercase text-white/30 px-1">
                <div className="col-span-5">Nombre</div><div className="col-span-2">Series</div><div className="col-span-2">Reps</div><div className="col-span-2">Kg</div>
              </div>
              {exercises.map((e, i) => (
                <div key={i} className="grid grid-cols-12 gap-2 items-center">
                  <input className="input col-span-5 text-sm" aria-label="Ejercicio" value={e.exercise_name} onChange={(ev) => updateExercise(i, 'exercise_name', ev.target.value)} placeholder="Sentadilla" />
                  <input type="number" min={0} className="input col-span-2 text-sm" aria-label="Series" value={e.sets} onChange={(ev) => updateExercise(i, 'sets', ev.target.value)} />
                  <input type="number" min={0} className="input col-span-2 text-sm" aria-label="Repeticiones" value={e.reps} onChange={(ev) => updateExercise(i, 'reps', ev.target.value)} />
                  <input type="number" min={0} step="0.5" className="input col-span-2 text-sm" aria-label="Kilos" value={e.weight_kg} onChange={(ev) => updateExercise(i, 'weight_kg', ev.target.value)} placeholder="—" />
                  <button type="button" onClick={() => setExercises(exercises.filter((_, x) => x !== i))} aria-label="Quitar ejercicio" className="text-white/25 hover:text-[#FF453A] text-xs">✕</button>
                </div>
              ))}
            </div>
            <button type="button" onClick={() => setExercises([...exercises, emptyExercise()])} className="mt-2 text-xs text-[#0A84FF] hover:underline">+ Agregar ejercicio</button>
          </div>
        )}

        <div>
          <label className="label" htmlFor="session-notes">Notas</label>
          <textarea id="session-notes" className="input min-h-[70px]" value={notes} onChange={(e) => setNotes(e.target.value)} />
        </div>
      </div>
    </Modal>
  )
}

// Un input según el tipo de campo. Un valor vacío no se guarda.
function FieldInput({ field, value, onChange }) {
  const id = `field-${field.id}`
  const label = <label className="label" htmlFor={id}>{field.name}{field.unit ? ` (${field.unit})` : ''}</label>

  if (field.type === 'numero') {
    return (
      <div>
        {label}
        <input id={id} type="number" step="any" className="input" value={value ?? ''}
          onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))} />
      </div>
    )
  }
  if (field.type === 'opcion') {
    return (
      <div>
        {label}
        <select id={id} className="input" value={value ?? ''} onChange={(e) => onChange(e.target.value || null)}>
          <option value="">—</option>
          {field.options.map((o) => <option key={o}>{o}</option>)}
        </select>
      </div>
    )
  }
  if (field.type === 'si_no' || field.type === 'escala') {
    const choices = field.type === 'si_no'
      ? [{ v: true, label: 'Sí' }, { v: false, label: 'No' }]
      : [1, 2, 3, 4, 5].map((n) => ({ v: n, label: '★'.repeat(n) }))
    return (
      <div>
        <span className="label" id={id}>{field.name}</span>
        <div className="flex gap-1.5" role="group" aria-labelledby={id}>
          {choices.map((c) => (
            <button key={String(c.v)} type="button" aria-pressed={value === c.v}
              onClick={() => onChange(value === c.v ? null : c.v)}
              className={`flex-1 py-2 rounded-xl text-xs font-semibold transition ${value === c.v ? 'bg-[#0A84FF] text-white' : 'bg-white/[0.06] text-white/50'}`}
            >{c.label}</button>
          ))}
        </div>
      </div>
    )
  }
  return (
    <div>
      {label}
      <input id={id} className="input" value={value ?? ''} maxLength={2000}
        onChange={(e) => onChange(e.target.value || null)} />
    </div>
  )
}
