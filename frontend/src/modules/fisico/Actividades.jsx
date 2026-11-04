import { useEffect, useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import { createActivity, updateActivity, deleteActivity, fetchActiveHabits } from './queries.js'
import { FIELD_TYPES } from './campos.js'

const COLORS = ['#BF5AF2', '#7C5CFF', '#2EBD85', '#FF9F0A', '#F6465D', '#5AC8FA']
const EMOJIS = ['🏋️', '🤸', '🏃', '🧘', '🥊', '🚴', '🏊', '⚽', '🧗', '🎾']
const TYPE_LABEL = Object.fromEntries(FIELD_TYPES.map((t) => [t.value, t.label]))

export default function Actividades({ activities, onChanged }) {
  const [editing, setEditing] = useState(null) // null = cerrado, {} = nueva, actividad = editar

  async function toggleActive(activity) {
    try {
      await updateActivity(activity.id, { active: !activity.active })
      toast.success(activity.active ? `${activity.name} en pausa` : `${activity.name} activa de nuevo`)
      onChanged()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Card
      title="Tus actividades"
      subtitle="Pausá las que no estés haciendo: su historial queda guardado"
      action={<Button size="sm" onClick={() => setEditing({})}>+ Actividad</Button>}
    >
      {!activities.length ? (
        <EmptyState icon="🏃" title="Sin actividades" description="Creá la primera: gym, correr, estiramientos…" />
      ) : (
        <ul className="divide-y divide-white/[0.04]">
          {activities.map((a) => {
            const fields = a.fields.filter((f) => !f.archived)
            return (
              <li key={a.id} className="py-3 flex items-center gap-3">
                <span className="w-9 h-9 rounded-xl grid place-items-center text-lg shrink-0" style={{ background: `${a.color || '#7C5CFF'}25` }}>
                  {a.emoji || '✨'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold flex items-center gap-2">
                    {a.name}
                    {!a.active && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-white/[0.08] text-white/50">PAUSADA</span>}
                  </div>
                  <div className="text-xs text-white/35 truncate">
                    {fields.length ? fields.map((f) => f.name).join(' · ') : 'Solo asistencia'}
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => toggleActive(a)}>{a.active ? 'Pausar' : 'Reactivar'}</Button>
                <Button variant="secondary" size="sm" onClick={() => setEditing(a)}>Editar</Button>
              </li>
            )
          })}
        </ul>
      )}

      <ActivityModal
        initial={editing}
        onClose={() => setEditing(null)}
        onSaved={onChanged}
      />
    </Card>
  )
}

const newField = () => ({ name: '', type: 'numero', unit: '', optionsText: '', archived: false })

// Pasa un campo guardado al formato del formulario (las opciones se editan como texto)
const toForm = (f) => ({ ...f, unit: f.unit || '', optionsText: (f.options || []).join(', ') })

function ActivityModal({ initial, onClose, onSaved }) {
  const open = initial !== null
  const isNew = !initial?.id
  const habitsQ = useAsync(() => (open ? fetchActiveHabits() : Promise.resolve([])), [open])
  const [form, setForm] = useState(null)

  useEffect(() => {
    if (!open) return
    setForm({
      name: initial.name || '',
      emoji: initial.emoji || '',
      color: initial.color || COLORS[0],
      habit_id: initial.habit_id || '',
      fields: (initial.fields || []).map(toForm)
    })
  }, [open, initial])

  if (!open || !form) return null

  const visible = form.fields.filter((f) => !f.archived)
  const archived = form.fields.filter((f) => f.archived)

  function setField(index, patch) {
    setForm({ ...form, fields: form.fields.map((f, i) => (i === index ? { ...f, ...patch } : f)) })
  }

  // Quitar un campo nuevo lo descarta; uno guardado queda archivado (el backend lo conserva)
  function removeField(index) {
    const field = form.fields[index]
    setForm({
      ...form,
      fields: field.id
        ? form.fields.map((f, i) => (i === index ? { ...f, archived: true } : f))
        : form.fields.filter((_, i) => i !== index)
    })
  }

  async function save() {
    const fields = form.fields.map(({ optionsText, ...f }) => ({
      ...f,
      name: f.name.trim(),
      unit: f.type === 'numero' && f.unit.trim() ? f.unit.trim() : null,
      options: f.type === 'opcion' ? optionsText.split(',').map((o) => o.trim()).filter(Boolean) : null
    }))
    if (!form.name.trim()) return toast.error('Ponele un nombre')
    if (fields.some((f) => !f.archived && !f.name)) return toast.error('Hay un campo sin nombre')

    const payload = {
      name: form.name.trim(),
      emoji: form.emoji || null,
      color: form.color,
      habit_id: form.habit_id || null,
      fields
    }
    try {
      if (isNew) await createActivity(payload)
      else await updateActivity(initial.id, payload)
      toast.success('Actividad guardada ✓')
      onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function remove() {
    if (!confirm(`¿Borrar "${initial.name}" y TODAS sus sesiones? Si solo querés dejar de verla, pausala.`)) return
    try {
      await deleteActivity(initial.id)
      toast.success('Actividad borrada')
      onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title={isNew ? 'Nueva actividad' : `Editar ${initial.name}`} size="lg"
      footer={
        <div className="flex justify-between gap-2">
          {!isNew ? <Button variant="danger" onClick={remove}>Borrar</Button> : <span />}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save}>Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="label" htmlFor="activity-name">Nombre</label>
          <input id="activity-name" className="input" value={form.name} maxLength={255}
            onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Calistenia, Correr…" />
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          <div>
            <span className="label">Emoji</span>
            <div className="flex gap-1.5 flex-wrap">
              {EMOJIS.map((e) => (
                <button key={e} type="button" aria-pressed={form.emoji === e}
                  onClick={() => setForm({ ...form, emoji: form.emoji === e ? '' : e })}
                  className={`w-9 h-9 rounded-xl text-lg transition ${form.emoji === e ? 'bg-white/[0.16]' : 'bg-white/[0.05]'}`}>{e}</button>
              ))}
            </div>
          </div>
          <div>
            <span className="label">Color</span>
            <div className="flex gap-2">
              {COLORS.map((c) => (
                <button key={c} type="button" aria-label={`Color ${c}`} aria-pressed={form.color === c}
                  onClick={() => setForm({ ...form, color: c })}
                  className={`w-8 h-8 rounded-full border-2 transition ${form.color === c ? 'border-white scale-110' : 'border-transparent'}`}
                  style={{ backgroundColor: c }} />
              ))}
            </div>
          </div>
        </div>

        <div>
          <label className="label" htmlFor="activity-habit">Hábito vinculado</label>
          <select id="activity-habit" className="input" value={form.habit_id}
            onChange={(e) => setForm({ ...form, habit_id: e.target.value })}>
            <option value="">Ninguno: la asistencia se marca en las sesiones</option>
            {(habitsQ.data || []).map((h) => <option key={h.id} value={h.id}>{h.emoji ? `${h.emoji} ` : ''}{h.name}</option>)}
          </select>
          <p className="text-[11px] text-white/30 mt-1.5">Con un hábito vinculado, marcar la asistencia acá también lo marca en el dashboard.</p>
        </div>

        <div>
          <span className="label">Qué anotás en cada sesión</span>
          <div className="space-y-2">
            {visible.length === 0 && <p className="text-xs text-white/30">Sin campos: solo se registra si fuiste.</p>}
            {form.fields.map((f, i) => f.archived ? null : (
              <div key={f.id || `nuevo-${i}`} className="p-3 rounded-xl bg-white/[0.04] space-y-2">
                <div className="flex gap-2">
                  <input className="input flex-1 text-sm" aria-label="Nombre del campo" value={f.name} maxLength={60}
                    onChange={(e) => setField(i, { name: e.target.value })} placeholder="Distancia, Sensación…" />
                  {/* Un campo guardado no cambia de tipo: sus valores viejos dejarían de tener sentido */}
                  <select className="input w-44 text-sm" aria-label="Tipo de campo" value={f.type} disabled={Boolean(f.id)}
                    onChange={(e) => setField(i, { type: e.target.value })}>
                    {FIELD_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                  <button type="button" onClick={() => removeField(i)} aria-label={`Quitar ${f.name || 'campo'}`}
                    className="px-2 text-white/30 hover:text-[#F6465D] text-sm">✕</button>
                </div>
                {f.type === 'numero' && (
                  <input className="input text-sm" aria-label="Unidad" value={f.unit} maxLength={20}
                    onChange={(e) => setField(i, { unit: e.target.value })} placeholder="Unidad (opcional): km, min…" />
                )}
                {f.type === 'opcion' && (
                  <input className="input text-sm" aria-label="Opciones separadas por coma" value={f.optionsText}
                    onChange={(e) => setField(i, { optionsText: e.target.value })} placeholder="Opciones separadas por coma: calle, pista, montaña" />
                )}
              </div>
            ))}
          </div>
          <button type="button" onClick={() => setForm({ ...form, fields: [...form.fields, newField()] })}
            className="mt-2 text-xs text-[#7C5CFF] hover:underline">+ Agregar campo</button>
        </div>

        {archived.length > 0 && (
          <div>
            <span className="label">Archivados</span>
            <p className="text-[11px] text-white/30 mb-2">No se cargan más, pero tus sesiones viejas los siguen mostrando.</p>
            <div className="flex flex-wrap gap-1.5">
              {form.fields.map((f, i) => !f.archived ? null : (
                <button key={f.id} type="button" onClick={() => setField(i, { archived: false })}
                  className="text-xs px-2.5 py-1.5 rounded-lg bg-white/[0.05] text-white/50 hover:text-white">
                  {f.name} · {TYPE_LABEL[f.type]} · Restaurar
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </Modal>
  )
}
