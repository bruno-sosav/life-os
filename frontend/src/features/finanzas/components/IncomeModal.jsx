import { useState } from 'react'
import { format, startOfMonth } from 'date-fns'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { createIncome } from '../api/ingresos.api.js'

export default function IncomeModal({ open, onClose, refDate, onSaved, sources }) {
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('')
  const [notes, setNotes] = useState('')

  async function save() {
    if (!amount || Number(amount) <= 0) return
    try {
      await createIncome({
        month: format(startOfMonth(refDate), 'yyyy-MM-dd'),
        amount: Number(amount),
        source: source.trim() || null,
        notes: notes.trim() || null
      })
      toast.success('Ingreso guardado')
      setAmount(''); setNotes(''); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo ingreso"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div>
          <label className="label">Monto ($)</label>
          <input type="number" min={0} className="input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="50000" />
        </div>
        <LabelPicker id="income-source" label="Fuente (opcional)" value={source} options={sources}
          onChange={setSource} placeholder="Elegí una o escribí una nueva: Sueldo, Freelance…" />
        <div>
          <label className="label">Notas (opcional)</label>
          <input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Sueldo enero, proyecto X…" />
        </div>
      </div>
    </Modal>
  )
}
