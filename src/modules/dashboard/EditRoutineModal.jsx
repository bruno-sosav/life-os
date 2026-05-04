import { useEffect, useState } from 'react'
import Modal from '../../components/Modal.jsx'
import Button from '../../components/Button.jsx'
import DrumPicker from '../../components/DrumPicker.jsx'
import { CATEGORY_COLORS, DAYS_LONG } from '../../lib/constants.js'
import { upsertRoutineBlock, deleteRoutineBlock } from './queries.js'
import { toast } from '../../store/toastStore.js'

const HOURS = Array.from({ length: 24 }, (_, i) => i)
const MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

const EMOJIS = ['🏋️', '🥊', '📖', '💼', '🍳', '🧘', '🏃', '☕', '💻', '🎯', '🛌', '🎵']
const empty = {
  day_of_week: 0, hour_start: 7, hour_min: 0, hour_end: 8, activity: '',
  category: 'personal', emoji: '', repeat_weekly: true, specific_date: ''
}

export default function EditRoutineModal({ open, onClose, initial, selectedDow, onSaved }) {
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    if (initial) {
      setForm({
        day_of_week: initial.day_of_week ?? selectedDow,
        hour_start: initial.hour_start ?? 7,
        hour_min: initial.hour_min ?? 0,
        hour_end: initial.hour_end ?? 8,
        activity: initial.activity ?? '',
        category: initial.category ?? 'personal',
        emoji: initial.emoji ?? '',
        repeat_weekly: initial.repeat_weekly ?? true,
        specific_date: initial.specific_date ?? ''
      })
    } else {
      setForm({ ...empty, day_of_week: selectedDow })
    }
  }, [open, initial?.id, selectedDow])

  async function save() {
    if (!form.activity.trim()) return
    try {
      await upsertRoutineBlock({
        ...(initial?.id ? { id: initial.id } : {}),
        day_of_week: form.repeat_weekly ? form.day_of_week : null,
        specific_date: !form.repeat_weekly && form.specific_date ? form.specific_date : null,
        repeat_weekly: form.repeat_weekly,
        hour_start: Number(form.hour_start),
        hour_min: Number(form.hour_min),
        hour_end: Number(form.hour_end),
        activity: form.activity.trim(),
        category: form.category,
        emoji: form.emoji || null,
        color: CATEGORY_COLORS[form.category] || CATEGORY_COLORS.default
      })
      toast.success(initial?.id ? 'Bloque actualizado ✓' : 'Bloque creado ✓')
      onSaved()
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  async function remove() {
    if (!initial?.id) return
    try {
      await deleteRoutineBlock(initial.id)
      toast.success('Bloque eliminado')
      onSaved()
      onClose()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  return (
    <Modal
      open={open} onClose={onClose}
      title={initial?.id ? 'Editar bloque' : 'Nuevo bloque de rutina'}
      footer={
        <div className="flex justify-between gap-2">
          {initial?.id ? <Button variant="danger" size="sm" onClick={remove}>Eliminar</Button> : <span />}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save}>Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-3">
        <div>
          <label className="label">Actividad</label>
          <input autoFocus className="input" value={form.activity} onChange={(e) => setForm({ ...form, activity: e.target.value })} placeholder="Gym, MMA, Trabajo…" />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Emoji</label>
            <div className="flex gap-1.5 flex-wrap">
              {EMOJIS.map((e) => (
                <button
                  key={e} type="button"
                  onClick={() => setForm({ ...form, emoji: form.emoji === e ? '' : e })}
                  className={`w-8 h-8 rounded-lg text-base grid place-items-center transition ${form.emoji === e ? 'bg-white/[0.15] ring-1 ring-white/20' : 'bg-white/[0.05] hover:bg-white/[0.1]'}`}
                >
                  {e}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Categoría</label>
            <select className="input" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
              {Object.keys(CATEGORY_COLORS).filter(k => k !== 'default').map((k) => (
                <option key={k} value={k}>{k}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label">Horario</label>
          <div className="flex items-end justify-center gap-1">
            <DrumPicker values={HOURS} selected={form.hour_start} onChange={(h) => setForm({ ...form, hour_start: h })} label="Inicio" />
            <span className="text-2xl font-bold text-white/30 pb-2">:</span>
            <DrumPicker values={MINUTES} selected={form.hour_min} onChange={(m) => setForm({ ...form, hour_min: m })} label="Min" />
            <span className="text-xs text-white/25 pb-3 px-2">hasta</span>
            <DrumPicker values={HOURS} selected={form.hour_end} onChange={(h) => setForm({ ...form, hour_end: h })} label="Fin" />
          </div>
        </div>

        <div>
          <label className="label">Repetición</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setForm({ ...form, repeat_weekly: true })}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${form.repeat_weekly ? 'bg-[#0A84FF] text-white' : 'bg-white/[0.06] text-white/50'}`}
            >
              Semanal ({DAYS_LONG[form.day_of_week]})
            </button>
            <button
              type="button"
              onClick={() => setForm({ ...form, repeat_weekly: false })}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${!form.repeat_weekly ? 'bg-[#0A84FF] text-white' : 'bg-white/[0.06] text-white/50'}`}
            >
              Solo ese día
            </button>
          </div>
        </div>

        {form.repeat_weekly ? (
          <div>
            <label className="label">Día de la semana</label>
            <select className="input" value={form.day_of_week} onChange={(e) => setForm({ ...form, day_of_week: Number(e.target.value) })}>
              {DAYS_LONG.map((d, i) => <option key={i} value={i}>{d}</option>)}
            </select>
          </div>
        ) : (
          <div>
            <label className="label">Fecha específica</label>
            <input type="date" className="input" value={form.specific_date} onChange={(e) => setForm({ ...form, specific_date: e.target.value })} />
          </div>
        )}
      </div>
    </Modal>
  )
}
