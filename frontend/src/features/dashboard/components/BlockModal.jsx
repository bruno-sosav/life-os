import { useEffect, useState } from 'react'
import Modal from '../../../shared/components/ui/Modal.jsx'
import Button from '../../../shared/components/ui/Button.jsx'
import DrumPicker from '../../../shared/components/forms/DrumPicker.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { deleteRoutineBlock, fetchBlockCategories, upsertRoutineBlock } from '../api/bloques.api.js'
import { toast } from '../../../shared/store/toastStore.js'

const DAYS_SHORT = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
const HOURS = Array.from({ length: 24 }, (_, i) => i)
const MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

const empty = {
  days_of_week: [], hour_start: 7, hour_min: 0, hour_end: 8, activity: '',
  category: '', emoji: '', repeat_weekly: true, specific_date: ''
}

export default function BlockModal({ open, onClose, initial, selectedWeekday, onSaved }) {
  const [form, setForm] = useState(empty)
  const categoriesQ = useAsync(() => (open ? fetchBlockCategories() : Promise.resolve([])), [open])

  useEffect(() => {
    if (!open) return
    if (initial) {
      setForm({
        days_of_week: initial.days_of_week ?? [selectedWeekday],
        hour_start: initial.hour_start ?? 7,
        hour_min: initial.hour_min ?? 0,
        hour_end: initial.hour_end ?? 8,
        activity: initial.activity ?? '',
        category: initial.category ?? '',
        emoji: initial.emoji ?? '',
        repeat_weekly: initial.repeat_weekly ?? true,
        specific_date: initial.specific_date ?? ''
      })
    } else {
      setForm({ ...empty, days_of_week: [selectedWeekday] })
    }
  }, [open, initial?.id, selectedWeekday])

  function toggleDay(i) {
    const cur = form.days_of_week
    setForm({ ...form, days_of_week: cur.includes(i) ? cur.filter(d => d !== i) : [...cur, i] })
  }

  async function save() {
    if (!form.activity.trim()) return
    // El backend valida y normaliza días/fecha según repeat_weekly
    try {
      await upsertRoutineBlock({
        ...(initial?.id ? { id: initial.id } : {}),
        days_of_week: form.days_of_week,
        specific_date: form.specific_date || null,
        repeat_weekly: form.repeat_weekly,
        hour_start: Number(form.hour_start),
        hour_min: Number(form.hour_min),
        hour_end: Number(form.hour_end),
        activity: form.activity.trim(),
        category: form.category.trim() || null,
        emoji: form.emoji || null
      })
      toast.success(initial?.id ? 'Bloque actualizado' : 'Bloque creado')
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
          <input className="input" value={form.activity} onChange={(e) => setForm({ ...form, activity: e.target.value })} placeholder="Trabajo, Facultad, Gym…" />
        </div>

        <LabelPicker id="block-category" label="Categoría (opcional)" value={form.category}
            onChange={(category) => setForm({ ...form, category })}
            options={categoriesQ.data || []} placeholder="Estudio, Trabajo…" />

        <div>
          <label className="label">Horario</label>
          <div className="flex items-end justify-center gap-1">
            <DrumPicker values={HOURS} selected={form.hour_start} onChange={(h) => setForm({ ...form, hour_start: h })} label="Inicio" />
            <span className="text-2xl font-bold text-ink-400 pb-2">:</span>
            <DrumPicker values={MINUTES} selected={form.hour_min} onChange={(m) => setForm({ ...form, hour_min: m })} label="Min" />
            <span className="text-xs text-ink-500 pb-3 px-2">hasta</span>
            <DrumPicker values={HOURS} selected={form.hour_end} onChange={(h) => setForm({ ...form, hour_end: h })} label="Fin" />
          </div>
        </div>

        <div>
          <label className="label">Repetición</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => setForm({ ...form, repeat_weekly: true })}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${form.repeat_weekly ? 'bg-accent text-ink-100' : 'bg-ink-700 text-ink-400'}`}
            >
              Semanal
            </button>
            <button
              type="button"
              onClick={() => setForm({ ...form, repeat_weekly: false })}
              className={`flex-1 py-2 rounded-xl text-sm font-semibold transition ${!form.repeat_weekly ? 'bg-accent text-ink-100' : 'bg-ink-700 text-ink-400'}`}
            >
              Solo ese día
            </button>
          </div>
        </div>

        {form.repeat_weekly ? (
          <div>
            <label className="label">Días</label>
            <div className="flex gap-1.5">
              {DAYS_SHORT.map((d, i) => {
                const active = form.days_of_week.includes(i)
                return (
                  <button
                    key={i} type="button"
                    onClick={() => toggleDay(i)}
                    className={`flex-1 h-9 rounded-xl text-xs font-bold transition ${active ? 'bg-accent text-ink-100' : 'bg-ink-700 text-ink-400'}`}
                  >
                    {d}
                  </button>
                )
              })}
            </div>
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
