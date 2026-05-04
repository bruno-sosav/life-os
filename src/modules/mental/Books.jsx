import { useMemo, useState, useEffect } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import { fmt, todayISO } from '../../lib/dates.js'
import { createBook, updateBook, deleteBook } from './queries.js'

const SHELVES = [
  { key: 'leyendo', label: '📖 Leyendo' },
  { key: 'pendiente', label: '📚 Pendientes' },
  { key: 'leido', label: '✅ Leídos' }
]

export default function Books({ books, onChange }) {
  const [editing, setEditing] = useState(null)
  const [adding, setAdding] = useState(false)

  const grouped = useMemo(() => {
    const g = { leyendo: [], pendiente: [], leido: [] }
    books.forEach((b) => g[b.status]?.push(b))
    return g
  }, [books])

  const yearRead = useMemo(() => {
    const year = new Date().getFullYear()
    return books.filter((b) => b.status === 'leido' && b.finished_at && new Date(b.finished_at).getFullYear() === year).length
  }, [books])

  return (
    <Card
      title="Biblioteca"
      subtitle={`${yearRead} libros leídos en ${new Date().getFullYear()}`}
      action={<Button size="sm" onClick={() => setAdding(true)}>+ Libro</Button>}
    >
      <div className="space-y-5">
        {SHELVES.map((shelf) => (
          <div key={shelf.key}>
            <h4 className="text-xs uppercase tracking-wider text-ink-400 font-semibold mb-2">
              {shelf.label} <span className="text-ink-500">· {grouped[shelf.key].length}</span>
            </h4>
            {grouped[shelf.key].length === 0 ? (
              <p className="text-xs text-ink-500 italic">Vacío</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {grouped[shelf.key].map((b) => (
                  <button
                    key={b.id}
                    onClick={() => setEditing(b)}
                    className="text-left bg-ink-800 border border-white/[0.05] rounded-lg p-3 hover:border-white/15 transition"
                  >
                    <div className="text-sm font-medium leading-tight">{b.title}</div>
                    {b.author && <div className="text-xs text-ink-400 mt-0.5">{b.author}</div>}
                    {b.rating ? (
                      <div className="text-xs mt-1.5 text-yellow-400">{'★'.repeat(b.rating)}<span className="text-ink-600">{'★'.repeat(5 - b.rating)}</span></div>
                    ) : null}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <BookModal
        open={adding || !!editing}
        onClose={() => { setAdding(false); setEditing(null) }}
        initial={editing}
        onSaved={() => { setAdding(false); setEditing(null); onChange() }}
        onDeleted={() => { setEditing(null); onChange() }}
      />
    </Card>
  )
}

function BookModal({ open, onClose, initial, onSaved, onDeleted }) {
  const empty = { title: '', author: '', status: 'pendiente', rating: 0, notes: '', started_at: '', finished_at: '' }
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
      finished_at: initial.finished_at || ''
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
      finished_at: form.status === 'leido' ? (form.finished_at || todayISO()) : (form.finished_at || null)
    }
    if (initial?.id) await updateBook(initial.id, payload)
    else await createBook(payload)
    onSaved()
  }

  async function remove() {
    if (initial?.id) {
      await deleteBook(initial.id)
      onDeleted?.()
    }
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
          <label className="label">Título</label>
          <input autoFocus className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Autor</label>
            <input className="input" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} />
          </div>
          <div>
            <label className="label">Estado</label>
            <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="pendiente">Pendiente</option>
              <option value="leyendo">Leyendo</option>
              <option value="leido">Leído</option>
            </select>
          </div>
        </div>
        <div>
          <label className="label">Rating</label>
          <div className="flex gap-1">
            {[1,2,3,4,5].map((n) => (
              <button
                type="button" key={n}
                onClick={() => setForm({ ...form, rating: form.rating === n ? 0 : n })}
                className={`text-2xl transition ${n <= form.rating ? 'text-yellow-400' : 'text-ink-600 hover:text-ink-400'}`}
              >★</button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Notas</label>
          <textarea className="input min-h-[80px]" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
      </div>
    </Modal>
  )
}
