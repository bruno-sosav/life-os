import { useEffect, useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fetchActiveHabits } from '../../../shared/api/habitos.api.js'
import { toast } from '../../../shared/store/toastStore.js'
import { createSkill, deleteSkill, updateSkill } from '../api/skills.api.js'
import { STAGES } from '../lib/tiempo.js'

// Crear (`skill` = {}) o editar una skill. La meta semanal se escribe en horas y minutos.
export default function SkillModal({ skill, types, onClose, onSaved }) {
  const open = skill !== null
  const isNew = !skill?.id
  const habitsQ = useAsync(() => (open ? fetchActiveHabits() : Promise.resolve([])), [open])
  const [form, setForm] = useState(null)

  useEffect(() => {
    if (!open) return
    const goal = skill.weekly_goal_min || 0
    setForm({
      name: skill.name || '',
      type: skill.type || '',
      stage: skill.stage || 'practicando',
      hours: goal ? String(Math.floor(goal / 60)) : '',
      minutes: goal ? String(goal % 60 || '') : '',
      habit_id: skill.habit_id || ''
    })
  }, [open, skill])

  if (!open || !form) return null
  const set = (patch) => setForm({ ...form, ...patch })

  async function save() {
    if (!form.name.trim()) return toast.error('Ponele un nombre')
    const goal = (Number(form.hours) || 0) * 60 + (Number(form.minutes) || 0)
    const payload = {
      name: form.name.trim(),
      type: form.type.trim() || null,
      stage: form.stage,
      weekly_goal_min: goal || null,
      habit_id: form.habit_id || null
    }
    try {
      if (isNew) await createSkill(payload)
      else await updateSkill(skill.id, payload)
      toast.success(isNew ? 'Skill creada' : 'Skill actualizada')
      onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function remove() {
    if (!confirm(`¿Borrar "${skill.name}" con todas sus prácticas? Si solo la dejaste, ponela en pausa.`)) return
    try {
      await deleteSkill(skill.id)
      toast.success('Skill borrada')
      onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title={isNew ? 'Nueva skill' : `Editar ${skill.name}`}
      footer={
        <div className="flex justify-between gap-2">
          {isNew ? <span /> : <Button variant="danger" size="sm" onClick={remove}>Borrar</Button>}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save}>Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="label" htmlFor="skill-name">Qué querés aprender</label>
          <input id="skill-name" className="input" value={form.name} maxLength={255} autoFocus
            onChange={(e) => set({ name: e.target.value })} placeholder="Ajedrez, Inglés, Ventas…" />
        </div>
        <LabelPicker id="skill-type" label="Tipo (opcional)" value={form.type} options={types}
          onChange={(type) => set({ type })} placeholder="Idioma, Hobby, Trabajo…" />
        <div>
          <span className="label">Etapa</span>
          <div className="grid grid-cols-3 gap-1.5">
            {STAGES.map((s) => (
              <button key={s.value} type="button" aria-pressed={form.stage === s.value} onClick={() => set({ stage: s.value })}
                className={`py-2 rounded-lg border text-xs font-semibold transition-colors ${
                  form.stage === s.value ? `bg-ink-700 border-ink-600 ${s.tone}` : 'border-ink-700 text-ink-400 hover:text-ink-100'
                }`}>{s.label}</button>
            ))}
          </div>
        </div>
        <div>
          <span className="label" id="skill-goal">Meta semanal (opcional)</span>
          <div className="flex items-center gap-2" role="group" aria-labelledby="skill-goal">
            <input type="number" min={0} max={168} className="input font-mono w-24" aria-label="Horas por semana"
              value={form.hours} onChange={(e) => set({ hours: e.target.value })} placeholder="0" />
            <span className="text-sm text-ink-400">h</span>
            <input type="number" min={0} max={59} step={5} className="input font-mono w-24" aria-label="Minutos por semana"
              value={form.minutes} onChange={(e) => set({ minutes: e.target.value })} placeholder="0" />
            <span className="text-sm text-ink-400">min por semana</span>
          </div>
        </div>
        <div>
          <label className="label" htmlFor="skill-habit">Hábito vinculado (opcional)</label>
          <select id="skill-habit" className="input" value={form.habit_id} onChange={(e) => set({ habit_id: e.target.value })}>
            <option value="">Ninguno</option>
            {(habitsQ.data || []).map((h) => <option key={h.id} value={h.id}>{h.name}</option>)}
          </select>
          <p className="text-[11px] text-ink-400 mt-1.5">Con un hábito vinculado, registrar una práctica lo marca en Hoy.</p>
        </div>
      </div>
    </Modal>
  )
}
