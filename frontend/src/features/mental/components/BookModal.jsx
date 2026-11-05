import { useEffect, useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import { todayISO } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { createBook, deleteBook, updateBook } from '../api/libros.api.js'

// Crear o editar un libro, y vincularlo a la skill para la que lo leés
export default function BookModal({ open, onClose, initial, skills, onSaved, onDeleted }) {
  const empty = { title: '', author: '', status: 'pendiente', rating: 0, notes: '', started_at: '', finished_at: '', skill_id: '' }
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    if (initial) setForm({
      title: initial.title || '',
      author: initial.author || '',
      status: initial.status || 'pendiente',
      rating: initial.rating || 0,
      notes: initial.notes || '',
      started_at: initial.started_at || '',
      finished_at: initial.finished_at || '',
      skill_id: initial.skill_id || ''
    })
    else setForm(empty)
  }, [open, initial?.id])

  async function save() {
    if (!form.title.trim()) return
    const payload = {
      title: form.title.trim(),
      author: form.author.trim() || null,
      status: form.status,
      rating: form.rating || null,
      notes: form.notes || null,
      started_at: form.started_at || null,
      finished_at: form.status === 'leido' ? (form.finished_at || todayISO()) : (form.finished_at || null),
      skill_id: form.skill_id || null
    }
    try {
      if (initial?.id) await updateBook(initial.id, payload)
      else await createBook(payload)
      onSaved()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function remove() {
    if (!initial?.id || !confirm(`¿Borrar "${initial.title}"?`)) return
    try {
      await deleteBook(initial.id)
      onDeleted?.()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={initial?.id ? 'Editar libro' : 'Nuevo libro'}
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
          <label className="label" htmlFor="book-title">Título</label>
          <input id="book-title" className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label" htmlFor="book-author">Autor</label>
            <input id="book-author" className="input" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
          </div>
          <div>
            <label className="label" htmlFor="book-status">Estado</label>
            <select id="book-status" className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="pendiente">Pendiente</option>
              <option value="leyendo">Leyendo</option>
              <option value="leido">Leído</option>
            </select>
          </div>
        </div>
        <div>
          <label className="label" htmlFor="book-skill">Para qué skill (opcional)</label>
          <select id="book-skill" className="input" value={form.skill_id} onChange={(e) => setForm({ ...form, skill_id: e.target.value })}>
            <option value="">Ninguna</option>
            {skills.map((sk) => <option key={sk.id} value={sk.id}>{sk.name}</option>)}
          </select>
        </div>
        <div>
          <span className="label">Rating</span>
          <div className="flex gap-1">
            {[1,2,3,4,5].map((n) => (
              <button
                type="button" key={n} aria-label={`${n} de 5`} aria-pressed={n <= form.rating}
                onClick={() => setForm({ ...form, rating: form.rating === n ? 0 : n })}
                className={`text-2xl transition ${n <= form.rating ? 'text-warn' : 'text-ink-600 hover:text-ink-400'}`}
              >★</button>
            ))}
          </div>
        </div>
        <div>
          <label className="label" htmlFor="book-notes">Notas</label>
          <textarea id="book-notes" className="input min-h-[80px]" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
      </div>
    </Modal>
  )
}
