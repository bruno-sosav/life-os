import { useEffect, useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'

// Editar el texto y la nota de un ítem de lista
export default function ItemModal({ item, onClose, onSave }) {
  const [form, setForm] = useState({ text: '', note: '' })
  useEffect(() => { if (item) setForm({ text: item.text, note: item.note || '' }) }, [item])

  function save() {
    if (!form.text.trim()) return
    onSave(item, { text: form.text.trim(), note: form.note.trim() || null })
    onClose()
  }

  return (
    <Modal open={item !== null} onClose={onClose} title="Editar ítem"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div>
          <label className="label" htmlFor="item-text">Texto</label>
          <input id="item-text" className="input" value={form.text} maxLength={255} autoFocus
            onChange={(e) => setForm({ ...form, text: e.target.value })} onKeyDown={(e) => e.key === 'Enter' && save()} />
        </div>
        <div>
          <label className="label" htmlFor="item-note">Nota (opcional)</label>
          <textarea id="item-note" className="input min-h-[80px]" value={form.note} maxLength={2000}
            onChange={(e) => setForm({ ...form, note: e.target.value })} placeholder="Talle M, la vi recomendada en…" />
        </div>
      </div>
    </Modal>
  )
}
