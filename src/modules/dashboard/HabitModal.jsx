import { useEffect, useState } from 'react'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import { createHabit, updateHabit, deleteHabit } from './queries.js'
import { toast } from '../../store/toastStore.js'

const COLORS = ['#30D158', '#BF5AF2', '#FF9F0A', '#FF453A', '#0A84FF', '#5AC8FA']
const EMOJIS = ['✨', '💧', '🏋️', '🥊', '📖', '🧘', '🍳', '💼', '🛌', '🏃', '🎯', '☕']
const DAYS_SHORT = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
const TIME_PRESETS = [
  { label: '🌅 Mañana', value: '08:00' },
  { label: '☀️ Tarde', value: '14:00' },
  { label: '🌙 Noche', value: '20:00' },
  { label: '🕐 Específica', value: 'custom' }
]

const empty = { name: '', color: COLORS[0], emoji: '', days_of_week: null, timeMode: 'mañana', start_time: '08:00', duration_min: 30 }

export default function HabitModal({ open, onClose, initial, onSaved }) {
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    if (initial) {
      const hasTime = !!initial.start_time
      setForm({
        name: initial.name || '',
        color: initial.color || COLORS[0],
        emoji: initial.emoji || '',
        days_of_week: initial.days_of_week || null,
        timeMode: hasTime ? 'custom' : 'sin',
        start_time: initial.start_time?.slice(0, 5) || '08:00',
        duration_min: initial.duration_min || 30
      })
    } else {
      setForm(empty)
    }
  }, [open, initial?.id])

  function toggleDay(d) {
    const cur = form.days_of_week || []
    const next = cur.includes(d) ? cur.filter((x) => x !== d) : [...cur, d].sort()
    setForm({ ...form, days_of_week: next.length === 7 || next.length === 0 ? null : next })
  }

  async function save() {
    if (!form.name.trim()) return
    const startTime = form.timeMode === 'sin' ? null : form.start_time
    const payload = {
      name: form.name.trim(),
      color: form.color,
      emoji: form.emoji || null,
      days_of_week: form.days_of_week,
      start_time: startTime,
      duration_min: startTime ? Number(form.duration_min) : null
    }
    try {
      if (initial?.id) await updateHabit(initial.id, payload)
      else await createHabit(payload)
      toast.success(initial?.id ? 'Hábito actualizado ✓' : 'Hábito creado ✓')
      onSaved()
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  async function remove() {
    if (!initial?.id) return
    if (!confirm('¿Eliminar este hábito?')) return
    try {
      await deleteHabit(initial.id)
      toast.success('Hábito eliminado')
      onSaved()
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  const activeDays = form.days_of_week || []

  return (
    <Modal
      open={open} onClose={onClose}
      title={initial?.id ? 'Editar hábito' : 'Nuevo hábito'}
      footer={
        <div className="flex justify-between gap-2">
          {initial?.id ? <Button variant="danger" size="sm" onClick={remove}>Eliminar</Button> : <span />}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save} color="green">Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="label">Nombre</label>
          <input autoFocus className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Meditar, Leer, Tomar agua…" />
        </div>

        <div>
          <label className="label">Días</label>
          <div className="flex gap-1.5">
            {DAYS_SHORT.map((d, i) => {
              const active = !form.days_of_week || activeDays.includes(i)
              return (
                <button
                  key={i} type="button"
                  onClick={() => toggleDay(i)}
                  className={`w-9 h-9 rounded-full text-xs font-bold transition-all ${active ? 'text-white' : 'bg-white/[0.06] text-white/30'}`}
                  style={active ? { background: form.color } : {}}
                >
                  {d}
                </button>
              )
            })}
          </div>
          <p className="text-[11px] text-white/30 mt-1.5">Sin selección = todos los días</p>
        </div>

        <div>
          <label className="label">Horario</label>
          <div className="grid grid-cols-4 gap-1.5 mb-3">
            {[{ label: '🌅 Mañana', value: '08:00' }, { label: '☀️ Tarde', value: '14:00' }, { label: '🌙 Noche', value: '20:00' }, { label: '🕐 Hora', value: 'custom' }].map((p) => (
              <button
                key={p.value} type="button"
                onClick={() => setForm({ ...form, timeMode: p.value === 'custom' ? 'custom' : 'preset', start_time: p.value === 'custom' ? form.start_time : p.value })}
                className={`py-2 px-1 rounded-xl text-[11px] font-semibold transition ${form.start_time === p.value || (p.value === 'custom' && form.timeMode === 'custom') ? 'bg-[#0A84FF] text-white' : 'bg-white/[0.06] text-white/50'}`}
              >
                {p.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setForm({ ...form, timeMode: 'sin', start_time: '' })}
            className={`text-xs px-3 py-1.5 rounded-lg mb-2 transition ${!form.start_time ? 'bg-white/[0.12] text-white' : 'text-white/30 hover:text-white/60'}`}
          >
            Sin horario fijo
          </button>
          {form.start_time && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label">Hora inicio</label>
                <input type="time" className="input" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
              </div>
              <div>
                <label className="label">Duración (min)</label>
                <input type="number" min={5} max={480} step={5} className="input" value={form.duration_min} onChange={(e) => setForm({ ...form, duration_min: Number(e.target.value) })} />
              </div>
            </div>
          )}
        </div>

        <div>
          <label className="label">Color</label>
          <div className="flex gap-2">
            {COLORS.map((c) => (
              <button key={c} type="button" onClick={() => setForm({ ...form, color: c })}
                className={`w-8 h-8 rounded-full border-2 transition ${form.color === c ? 'border-white scale-110' : 'border-transparent'}`}
                style={{ backgroundColor: c }} />
            ))}
          </div>
        </div>

        <div>
          <label className="label">Emoji (opcional)</label>
          <div className="flex gap-1.5 flex-wrap">
            {EMOJIS.map((e) => (
              <button key={e} type="button" onClick={() => setForm({ ...form, emoji: form.emoji === e ? '' : e })}
                className={`w-9 h-9 rounded-lg text-lg grid place-items-center transition ${form.emoji === e ? 'bg-white/[0.15] ring-1 ring-white/20' : 'bg-white/[0.05] hover:bg-white/[0.1]'}`}>
                {e}
              </button>
            ))}
          </div>
        </div>
      </div>
    </Modal>
  )
}
