import { useEffect, useState } from 'react'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import DrumPicker from '../../components/DrumPicker.jsx'
import { createHabit, updateHabit, deleteHabit } from './queries.js'
import { toast } from '../../store/toastStore.js'

const COLORS = ['#30D158', '#BF5AF2', '#FF9F0A', '#FF453A', '#0A84FF', '#5AC8FA']
const EMOJIS = ['✨', '💧', '🏋️', '🥊', '📖', '🧘', '🍳', '💼', '🛌', '🏃', '🎯', '☕']
const DAYS_SHORT = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
const HOURS = Array.from({ length: 24 }, (_, i) => i)
const MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

const empty = { name: '', color: COLORS[0], emoji: '', days_of_week: null, hasTime: false, hour: 8, minute: 0, duration_min: 30, linked_module: null }

export default function HabitModal({ open, onClose, initial, onSaved }) {
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    if (initial) {
      const parts = initial.start_time?.slice(0, 5).split(':').map(Number)
      setForm({
        name: initial.name || '',
        color: initial.color || COLORS[0],
        emoji: initial.emoji || '',
        days_of_week: initial.days_of_week || null,
        hasTime: !!initial.start_time,
        hour: parts?.[0] ?? 8,
        minute: parts?.[1] ?? 0,
        duration_min: initial.duration_min || 30,
        linked_module: initial.linked_module || null
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
    const startTime = form.hasTime
      ? `${String(form.hour).padStart(2, '0')}:${String(form.minute).padStart(2, '0')}`
      : null
    const payload = {
      name: form.name.trim(),
      color: form.color,
      emoji: form.emoji || null,
      days_of_week: form.days_of_week,
      start_time: startTime,
      duration_min: startTime ? Number(form.duration_min) : null,
      linked_module: form.linked_module || null
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
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Meditar, Leer, Tomar agua…" />
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
          <div className="flex items-center justify-between mb-3">
            <label className="label mb-0">Horario</label>
            <button
              type="button"
              onClick={() => setForm({ ...form, hasTime: !form.hasTime })}
              className={`text-xs px-3 py-1 rounded-full font-semibold transition ${form.hasTime ? 'bg-[#0A84FF] text-white' : 'bg-white/[0.08] text-white/40'}`}
            >
              {form.hasTime ? 'Con horario' : 'Sin horario fijo'}
            </button>
          </div>
          {form.hasTime && (
            <div className="space-y-3">
              <div className="flex items-center justify-center gap-2">
                <DrumPicker values={HOURS} selected={form.hour} onChange={(h) => setForm({ ...form, hour: h })} label="Hora" />
                <span className="text-2xl font-bold text-white/40 mt-5">:</span>
                <DrumPicker values={MINUTES} selected={form.minute} onChange={(m) => setForm({ ...form, minute: m })} label="Min" />
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
          <label className="label">Sincronizar con pestaña</label>
          <div className="flex gap-1.5">
            {[{ label: 'Ninguna', v: null }, { label: '🏋️ Gym', v: 'gym' }, { label: '🥊 MMA', v: 'mma' }].map((opt) => (
              <button
                key={String(opt.v)} type="button"
                onClick={() => setForm({ ...form, linked_module: opt.v })}
                className={`flex-1 py-2 rounded-xl text-xs font-semibold transition ${form.linked_module === opt.v ? 'bg-[#BF5AF2] text-white' : 'bg-white/[0.06] text-white/40'}`}
              >{opt.label}</button>
            ))}
          </div>
          <p className="text-[11px] text-white/30 mt-1.5">Al marcar este hábito como hecho, también aparece en la pestaña correspondiente</p>
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
