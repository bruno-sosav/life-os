import { useState } from 'react'
import { format } from 'date-fns'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import LabelPicker from '../../../shared/components/forms/LabelPicker.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { createExpense } from '../api/gastos.api.js'

export default function ExpenseModal({ open, onClose, onSaved, categories }) {
  const today = format(new Date(), 'yyyy-MM-dd')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(today)

  async function save() {
    if (!amount || Number(amount) <= 0) return
    if (!category.trim()) return toast.error('Elegí o escribí una categoría')
    try {
      await createExpense({
        date,
        amount: Number(amount),
        category: category.trim(),
        description: description.trim() || null
      })
      toast.success('Gasto guardado')
      setAmount(''); setDescription(''); setDate(today); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo gasto"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Monto ($)</label>
            <input type="number" min={0} className="input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="1500" />
          </div>
          <div>
            <label className="label">Fecha</label>
            <input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
        </div>
        <LabelPicker id="expense-category" label="Categoría" value={category} options={categories}
          onChange={setCategory} placeholder="Elegí una o escribí una nueva: 🍔 Comida" />
        <div>
          <label className="label">Descripción (opcional)</label>
          <input className="input" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Almuerzo, nafta, Netflix…" />
        </div>
      </div>
    </Modal>
  )
}
