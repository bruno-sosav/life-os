import { useEffect, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import { format, startOfMonth } from 'date-fns'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import SaveSteps from '../../../shared/components/feedback/SaveSteps.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { createIncome } from '../api/ingresos.api.js'
import { money } from '../lib/dinero.js'

// Cargar un ingreso del mes que estás viendo, con el mismo flujo que un gasto
export default function IncomeModal({ open, onClose, refDate, onSaved, sources }) {
  const [step, setStep] = useState('form')
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('')
  const [notes, setNotes] = useState('')
  const [saved, setSaved] = useState(null)

  useEffect(() => {
    if (!open) return
    setStep('form'); setAmount(''); setSource(''); setNotes(''); setSaved(null)
  }, [open])

  const value = Number(amount) || 0

  async function save() {
    if (value <= 0) return
    setStep('saving')
    try {
      const created = await createIncome({
        month: format(startOfMonth(refDate), 'yyyy-MM-dd'),
        amount: value,
        source: source.trim() || null,
        notes: notes.trim() || null
      })
      setSaved(created)
      setStep('done')
    } catch (e) {
      setStep('form')
      toast.error('Error: ' + e.message)
    }
  }

  function close() {
    if (saved) onSaved(saved)
    onClose()
  }

  return (
    <Modal open={open} onClose={close} title="Cargar ingreso"
      footer={step === 'form' ? (
        <div className="grid grid-cols-2 gap-2">
          <Button variant="ghost" onClick={close}>Cancelar</Button>
          <Button onClick={save} disabled={value <= 0}>{value ? `Guardar ${money(value)}` : 'Guardar'}</Button>
        </div>
      ) : step === 'done' ? (
        <div className="flex justify-end"><Button onClick={close}>Listo</Button></div>
      ) : null}
    >
      <AnimatePresence mode="wait">
        {step === 'form' ? (
          <div key="form" className="space-y-4">
            <div>
              <label className="label" htmlFor="income-amount">Monto</label>
              <div className="flex items-center gap-2 rounded-xl bg-ink-900 border border-ink-600 focus-within:border-accent px-3.5 transition-colors">
                <span className="font-mono text-ink-400">$</span>
                <input id="income-amount" type="number" min={0} inputMode="numeric" autoFocus
                  className="flex-1 bg-transparent py-3 font-mono text-lg font-semibold focus:outline-none placeholder:text-ink-500"
                  value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0"
                  onKeyDown={(e) => e.key === 'Enter' && save()} />
              </div>
            </div>
            <LabelPicker id="income-source" label="Fuente (opcional)" value={source} options={sources}
              onChange={setSource} placeholder="Elegí una o escribí una nueva: Sueldo, Freelance…" />
            <div>
              <label className="label" htmlFor="income-notes">Notas (opcional)</label>
              <input id="income-notes" className="input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Sueldo de enero, proyecto X…" />
            </div>
          </div>
        ) : (
          <SaveSteps key={step} step={step} savingText="Guardando ingreso…" doneTitle="Ingreso guardado"
            doneText={saved && `Se cargaron ${money(saved.amount)}${saved.source ? ` de ${saved.source}` : ''}.`} />
        )}
      </AnimatePresence>
    </Modal>
  )
}
