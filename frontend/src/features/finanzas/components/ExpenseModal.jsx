import { useEffect, useState } from 'react'
import { AnimatePresence } from 'framer-motion'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import SaveSteps from '../../../shared/components/feedback/SaveSteps.jsx'
import { todayISO } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { createExpense } from '../api/gastos.api.js'
import { money } from '../lib/dinero.js'

// Cargar un gasto: mientras escribís ves cuánto de lo que te queda se lleva; al guardar,
// "guardando…" y después el éxito. `left` es lo que te queda este mes (lo calcula el backend).
export default function ExpenseModal({ open, onClose, onSaved, categories, left }) {
  const [step, setStep] = useState('form') // form → saving → done
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(todayISO())
  const [saved, setSaved] = useState(null)

  useEffect(() => {
    if (!open) return
    setStep('form'); setAmount(''); setCategory(''); setDescription(''); setDate(todayISO()); setSaved(null)
  }, [open])

  const value = Number(amount) || 0
  const hasRoom = left > 0
  const share = hasRoom ? Math.min(value / left, 1) : value > 0 ? 1 : 0
  const tooMuch = value > 0 && value > left
  const hint = !value ? 'Ingresá el monto'
    : tooMuch ? 'Te pasás de lo que te queda este mes'
      : !category.trim() ? 'Elegí o escribí una categoría'
        : `Te quedarían ${money(left - value)}`
  const ready = value > 0 && category.trim()

  async function save() {
    if (!ready) return
    setStep('saving')
    try {
      const created = await createExpense({ date, amount: value, category: category.trim(), description: description.trim() || null })
      setSaved(created)
      setStep('done')
    } catch (e) {
      setStep('form')
      toast.error('Error: ' + e.message)
    }
  }

  // El tablero se actualiza al cerrar el éxito, así la fila nueva aparece con su destello
  function close() {
    if (saved) onSaved(saved)
    onClose()
  }

  return (
    <Modal open={open} onClose={close} title="Cargar gasto"
      footer={step === 'form' ? (
        <div className="grid grid-cols-2 gap-2">
          <Button variant="ghost" onClick={close}>Cancelar</Button>
          <Button onClick={save} disabled={!ready}>{value ? `Guardar ${money(value)}` : 'Guardar'}</Button>
        </div>
      ) : step === 'done' ? (
        <div className="flex justify-end"><Button onClick={close}>Listo</Button></div>
      ) : null}
    >
      <AnimatePresence mode="wait">
        {step === 'form' ? (
          <div key="form" className="space-y-4">
            <div className={`rounded-xl border px-3.5 py-3 flex items-center justify-between ${hasRoom ? 'bg-up/[0.06] border-up/20' : 'bg-down/[0.06] border-down/20'}`}>
              <span className={`text-[10px] font-bold tracking-wider uppercase ${hasRoom ? 'text-up' : 'text-down'}`}>Te queda este mes</span>
              <span className={`font-mono text-base font-bold ${hasRoom ? 'text-up' : 'text-down'}`}>{money(left)}</span>
            </div>

            <div>
              <label className="label" htmlFor="expense-amount">Monto</label>
              <div className="flex items-center gap-2 rounded-xl bg-ink-900 border border-ink-600 focus-within:border-accent px-3.5 transition-colors">
                <span className="font-mono text-ink-400">$</span>
                <input id="expense-amount" type="number" min={0} inputMode="numeric" autoFocus
                  className="flex-1 bg-transparent py-3 font-mono text-lg font-semibold focus:outline-none placeholder:text-ink-500"
                  value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="0"
                  onKeyDown={(e) => e.key === 'Enter' && save()} />
              </div>
              <div className="h-[3px] bg-ink-700 rounded-full overflow-hidden mt-2" aria-hidden="true">
                <div className={`h-full rounded-full transition-all duration-300 ${tooMuch ? 'bg-down' : 'bg-up'}`} style={{ width: `${share * 100}%` }} />
              </div>
              <div className="flex justify-between text-[11px] mt-1.5">
                <span className={tooMuch ? 'text-down' : 'text-ink-400'} aria-live="polite">{hint}</span>
                {value > 0 && hasRoom && <span className="font-mono text-ink-400">{Math.round(share * 100)}% de lo que queda</span>}
              </div>
            </div>

            <LabelPicker id="expense-category" label="Categoría" value={category} options={categories}
              onChange={setCategory} placeholder="Elegí una o escribí una nueva: Comida, Nafta…" />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="label" htmlFor="expense-description">Descripción (opcional)</label>
                <input id="expense-description" className="input" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Supermercado…" />
              </div>
              <div>
                <label className="label" htmlFor="expense-date">Fecha</label>
                <input id="expense-date" type="date" className="input font-mono" value={date} onChange={(e) => setDate(e.target.value)} />
              </div>
            </div>
          </div>
        ) : (
          <SaveSteps key={step} step={step} savingText="Guardando gasto…" doneTitle="Gasto guardado"
            doneText={saved && `Se cargó ${money(saved.amount)} en ${saved.category}.`} />
        )}
      </AnimatePresence>
    </Modal>
  )
}
