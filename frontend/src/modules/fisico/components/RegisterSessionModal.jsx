import { useEffect, useState } from 'react'
import Button from '../../../components/Button.jsx'
import Modal from '../../../components/Modal.jsx'
import { PICK_COLORS } from '../../../lib/constants.js'
import { fmt, todayISO } from '../../../lib/dates.js'
import { toast } from '../../../store/toastStore.js'
import { createActivity } from '../api/actividades.api.js'
import { createSession, fetchExerciseNames, fetchLastExercise } from '../api/sesiones.api.js'
import { hasExercises } from '../campos.js'
import FieldInput from './FieldInput.jsx'

const emptyExercise = () => ({ exercise_name: '', sets: 3, reps: 10, weight_kg: '', last: undefined })

// "3×10 · 60 kg" de cada serie de la última vez
const describe = (sets) =>
  sets.map((s) => `${s.sets ?? '—'}×${s.reps ?? '—'}${s.weight_kg != null ? ` · ${s.weight_kg} kg` : ''}`).join(', ')

export default function RegisterSessionModal({ open, activities, onClose, onSaved, onTypeCreated }) {
  const [activityId, setActivityId] = useState(null)
  const [date, setDate] = useState(todayISO())
  const [values, setValues] = useState({})
  const [notes, setNotes] = useState('')
  const [exercises, setExercises] = useState([emptyExercise()])
  const [names, setNames] = useState([])
  const [newType, setNewType] = useState(null) // null = no se está creando; string = el nombre

  useEffect(() => {
    if (!open) return
    setActivityId((current) => current && activities.some((a) => a.id === current) ? current : activities[0]?.id ?? null)
    setDate(todayISO()); setValues({}); setNotes(''); setExercises([emptyExercise()]); setNewType(null)
    fetchExerciseNames().then(setNames).catch(() => setNames([]))
  }, [open]) // eslint-disable-line react-hooks/exhaustive-deps

  const activity = activities.find((a) => a.id === activityId)
  const fields = activity ? activity.fields.filter((f) => !f.archived && f.type !== 'ejercicios') : []
  const withExercises = activity ? hasExercises(activity) : false

  function setExercise(i, patch) {
    setExercises((list) => list.map((e, x) => (x === i ? { ...e, ...patch } : e)))
  }

  // Al terminar de escribir el nombre, trae lo que hiciste la última vez
  async function lookUp(i, name) {
    if (!name.trim()) return setExercise(i, { last: undefined })
    try { setExercise(i, { last: await fetchLastExercise(name) }) } catch { /* sin pista */ }
  }

  async function createType() {
    const name = (newType || '').trim()
    if (!name) return
    try {
      const created = await createActivity({
        name,
        color: PICK_COLORS[activities.length % PICK_COLORS.length],
        fields: [{ name: 'Ejercicios', type: 'ejercicios' }]
      })
      await onTypeCreated()
      setActivityId(created.id)
      setNewType(null)
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function save() {
    if (!activity) return toast.error('Elegí qué entrenaste')
    try {
      await createSession({
        activity_id: activity.id,
        date,
        attended: true,
        notes: notes.trim() || null,
        values,
        exercises: withExercises
          ? exercises.filter((e) => e.exercise_name.trim()).map((e) => ({
            exercise_name: e.exercise_name.trim(),
            sets: e.sets === '' ? null : Number(e.sets),
            reps: e.reps === '' ? null : Number(e.reps),
            weight_kg: e.weight_kg === '' ? null : Number(e.weight_kg)
          }))
          : []
      })
      toast.success(`${activity.name} registrado`)
      onSaved()
      onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Registrar entrenamiento" size="lg"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-4">
        <div>
          <span className="label">Qué entrenaste</span>
          <div className="flex flex-wrap gap-1.5">
            {activities.map((a) => {
              const on = a.id === activityId
              return (
                <button key={a.id} type="button" aria-pressed={on} onClick={() => setActivityId(a.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-semibold transition-colors ${
                    on ? 'bg-ink-700 border-ink-600 text-ink-100' : 'border-ink-700 text-ink-400 hover:text-ink-100'
                  }`}>
                  <span className="w-2 h-2 rounded-full" style={{ background: a.color || PICK_COLORS[5] }} />
                  {a.name}
                </button>
              )
            })}
            {newType === null ? (
              <button type="button" onClick={() => setNewType('')}
                className="px-3 py-2 rounded-lg border border-dashed border-ink-600 text-sm font-semibold text-ink-400 hover:text-up hover:border-up/40 transition">
                + Nuevo tipo
              </button>
            ) : (
              <div className="flex gap-1.5">
                <input className="input !py-2 w-40" autoFocus value={newType} maxLength={255} aria-label="Nombre del tipo nuevo"
                  placeholder="Calistenia…" onChange={(e) => setNewType(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') createType(); if (e.key === 'Escape') setNewType(null) }} />
                <Button size="sm" onClick={createType}>Crear</Button>
              </div>
            )}
          </div>
        </div>

        <div>
          <label className="label" htmlFor="session-date">Fecha</label>
          <input id="session-date" type="date" className="input font-mono" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>

        {fields.map((f) => (
          <FieldInput key={f.id} field={f} value={values[f.id]} onChange={(v) => setValues({ ...values, [f.id]: v })} />
        ))}

        {withExercises && (
          <div>
            <span className="label">Ejercicios</span>
            <datalist id="exercise-names">{names.map((n) => <option key={n} value={n} />)}</datalist>
            <div className="space-y-2">
              <div className="grid grid-cols-12 gap-2 text-[10px] uppercase tracking-wider text-ink-400 font-semibold px-1">
                <span className="col-span-5">Nombre</span><span className="col-span-2">Series</span><span className="col-span-2">Reps</span><span className="col-span-2">Kg</span>
              </div>
              {exercises.map((e, i) => (
                <div key={i}>
                  <div className="grid grid-cols-12 gap-2 items-center">
                    <input className="input col-span-5 text-sm" list="exercise-names" aria-label="Ejercicio" placeholder="Sentadilla"
                      value={e.exercise_name} onChange={(ev) => setExercise(i, { exercise_name: ev.target.value })}
                      onBlur={(ev) => lookUp(i, ev.target.value)} />
                    <input type="number" min={0} className="input col-span-2 text-sm font-mono" aria-label="Series" value={e.sets} onChange={(ev) => setExercise(i, { sets: ev.target.value })} />
                    <input type="number" min={0} className="input col-span-2 text-sm font-mono" aria-label="Repeticiones" value={e.reps} onChange={(ev) => setExercise(i, { reps: ev.target.value })} />
                    <input type="number" min={0} step="0.5" className="input col-span-2 text-sm font-mono" aria-label="Kilos" placeholder="—" value={e.weight_kg} onChange={(ev) => setExercise(i, { weight_kg: ev.target.value })} />
                    <button type="button" onClick={() => setExercises(exercises.filter((_, x) => x !== i))} aria-label="Quitar ejercicio"
                      className="col-span-1 h-10 rounded-lg text-ink-400 hover:text-down hover:bg-ink-700 text-xs">✕</button>
                  </div>
                  {e.last && (
                    <p className="text-[11px] text-ink-400 mt-1 px-1">
                      Última vez <span className="font-mono">{fmt(e.last.date, 'd MMM')}</span>: <span className="font-mono text-ink-300">{describe(e.last.sets)}</span>
                    </p>
                  )}
                  {e.last === null && <p className="text-[11px] text-ink-400 mt-1 px-1">Primera vez con este ejercicio</p>}
                </div>
              ))}
            </div>
            <button type="button" onClick={() => setExercises([...exercises, emptyExercise()])} className="mt-2 text-xs font-semibold text-up hover:underline">
              + Agregar ejercicio
            </button>
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
