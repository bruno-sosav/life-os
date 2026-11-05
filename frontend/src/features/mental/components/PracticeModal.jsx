import { useEffect, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import SaveSteps from '../../../shared/components/feedback/SaveSteps.jsx'
import { todayISO } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { createPractice } from '../api/practicas.api.js'
import { hm } from '../lib/tiempo.js'

const QUICK = [15, 30, 45, 60]

// Registrar práctica: qué, cuánto y cómo te deja contra la meta de la semana
export default function PracticeModal({ open, skills, initialSkill, onClose, onSaved }) {
  const [step, setStep] = useState('form')
  const [skillId, setSkillId] = useState(null)
  const [minutes, setMinutes] = useState(30)
  const [custom, setCustom] = useState('')
  const [date, setDate] = useState(todayISO())
  const [note, setNote] = useState('')

  useEffect(() => {
    if (!open) return
    setStep('form'); setMinutes(30); setCustom(''); setDate(todayISO()); setNote('')
    setSkillId(initialSkill ?? skills[0]?.id ?? null)
  }, [open]) // eslint-disable-line react-hooks/exhaustive-deps

  const skill = skills.find((s) => s.id === skillId)
  const value = custom ? Number(custom) || 0 : minutes
  const after = (skill?.week_minutes ?? 0) + value
  const goal = skill?.weekly_goal_min
  const hint = !skill ? 'Creá una skill primero'
    : !goal ? 'Esta skill no tiene meta semanal'
      : after >= goal ? `Con esto llegás a ${hm(after)} de ${hm(goal)}: meta cumplida`
        : `Con esto llevás ${hm(after)} de ${hm(goal)} esta semana`

  async function save() {
    if (!skill || value < 1) return
    setStep('saving')
    try {
      await createPractice({ skill_id: skill.id, date, minutes: value, note: note.trim() || null })
      setStep('done')
    } catch (e) {
      setStep('form')
      toast.error('Error: ' + e.message)
    }
  }

  function close() {
    if (step === 'done') onSaved(skill.id)
    onClose()
  }

  return (
    <Modal open={open} onClose={close} title="Registrar práctica"
      footer={step === 'form' ? (
        <div className="grid grid-cols-2 gap-2">
          <Button variant="ghost" onClick={close}>Cancelar</Button>
          <Button onClick={save} disabled={!skill || value < 1}>Guardar {value ? hm(value) : ''}</Button>
        </div>
      ) : step === 'done' ? (
        <div className="flex justify-end"><Button onClick={close}>Listo</Button></div>
      ) : null}
    >
      <AnimatePresence mode="wait">
        {step === 'form' ? (
          <div key="form" className="space-y-4">
            <div>
              <span className="label">Qué practicaste</span>
              <div className="flex flex-wrap gap-1.5">
                {skills.map((s) => (
                  <button key={s.id} type="button" aria-pressed={s.id === skillId} onClick={() => setSkillId(s.id)}
                    className={`px-3 py-2 rounded-lg border text-sm font-semibold transition-colors ${
                      s.id === skillId ? 'bg-up/15 border-up/40 text-up' : 'border-ink-600 text-ink-300 hover:text-ink-100'
                    }`}>{s.name}</button>
                ))}
              </div>
            </div>
            <div>
              <span className="label">Cuánto tiempo</span>
              <div className="grid grid-cols-5 gap-1.5">
                {QUICK.map((m) => {
                  const on = !custom && minutes === m
                  return (
                    <button key={m} type="button" aria-pressed={on} onClick={() => { setMinutes(m); setCustom('') }}
                      className={`h-11 rounded-lg border font-mono text-sm font-bold transition-colors ${
                        on ? 'bg-up/15 border-up/40 text-up' : 'border-ink-600 text-ink-300 hover:text-ink-100'
                      }`}>{m}′</button>
                  )
                })}
                <input type="number" min={1} max={1440} inputMode="numeric" aria-label="Otros minutos" placeholder="otro"
                  className={`h-11 rounded-lg border bg-ink-900 text-center font-mono text-sm focus:outline-none focus:border-accent ${custom ? 'border-up/40 text-up' : 'border-ink-600'}`}
                  value={custom} onChange={(e) => setCustom(e.target.value)} />
              </div>
              <p className="text-[11px] text-ink-400 mt-2" aria-live="polite">{hint}</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label" htmlFor="practice-note">Qué hiciste (opcional)</label>
                <input id="practice-note" className="input" value={note} maxLength={2000} onChange={(e) => setNote(e.target.value)} placeholder="Táctica, vocabulario…" />
              </div>
              <div>
                <label className="label" htmlFor="practice-date">Fecha</label>
                <input id="practice-date" type="date" className="input font-mono" value={date} onChange={(e) => setDate(e.target.value)} />
              </div>
            </div>
          </div>
        ) : (
          <SaveSteps key={step} step={step} savingText="Guardando práctica…" doneTitle="Práctica guardada"
            doneText={skill && `Sumaste ${hm(value)} de ${skill.name}.${skill.habit_id ? ' Su hábito ya quedó marcado en Hoy.' : ''}`} />
        )}
      </AnimatePresence>
    </Modal>
  )
}
