import { useEffect, useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import { PICK_COLORS } from '../../../shared/lib/constants.js'
import { toast } from '../../../shared/store/toastStore.js'
import { createList, deleteList, updateList } from '../api/listas.api.js'

// Crear (`list` = {}) o editar una lista: nombre, color y si es para aprender
export default function ListModal({ list, onClose, onSaved, onDeleted }) {
  const open = list !== null
  const isNew = !list?.id
  const [form, setForm] = useState({ name: '', color: PICK_COLORS[0], for_learning: false })

  useEffect(() => {
    if (!open) return
    setForm({ name: list.name || '', color: list.color || PICK_COLORS[0], for_learning: !!list.for_learning })
  }, [open, list])

  async function save() {
    if (!form.name.trim()) return toast.error('Ponele un nombre')
    const payload = { ...form, name: form.name.trim() }
    try {
      const saved = isNew ? await createList(payload) : await updateList(list.id, payload)
      onSaved(saved)
      onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function remove() {
    if (!confirm(`¿Borrar "${list.name}" con todos sus ítems?`)) return
    try {
      await deleteList(list.id)
      toast.success('Lista borrada')
      onDeleted()
      onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title={isNew ? 'Nueva lista' : 'Editar lista'}
      footer={
        <div className="flex justify-between gap-2">
          {isNew ? <span /> : <Button variant="danger" size="sm" onClick={remove}>Borrar lista</Button>}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save}>{isNew ? 'Crear' : 'Guardar'}</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-4">
        <div>
          <label className="label" htmlFor="list-name">Nombre</label>
          <input id="list-name" className="input" value={form.name} maxLength={255} autoFocus
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && save()} placeholder="Próximas compras, Películas, Quiero aprender…" />
        </div>
        <div>
          <span className="label">Color</span>
          <div className="flex gap-2">
            {PICK_COLORS.map((c) => (
              <button key={c} type="button" aria-label={`Color ${c}`} aria-pressed={form.color === c}
                onClick={() => setForm({ ...form, color: c })}
                className={`w-8 h-8 rounded-full border-2 transition ${form.color === c ? 'border-ink-100 scale-110' : 'border-transparent'}`}
                style={{ backgroundColor: c }} />
            ))}
          </div>
        </div>
        <label className="flex items-start gap-3 cursor-pointer rounded-xl border border-ink-700 p-3 hover:border-ink-600">
          <input type="checkbox" className="mt-0.5 w-4 h-4 accent-accent" checked={form.for_learning}
            onChange={(e) => setForm({ ...form, for_learning: e.target.checked })} />
          <span>
            <span className="block text-sm font-semibold">Es para aprender</span>
            <span className="block text-xs text-ink-400 mt-0.5">Sus ítems muestran "Practicar →" para pasarlos a Aprender.</span>
          </span>
        </label>
      </div>
    </Modal>
  )
}
