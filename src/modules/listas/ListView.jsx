import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchList, fetchListItems, createItem, updateItem, deleteItem } from './queries.js'

const STATUSES = [
  { value: 'pendiente', label: 'Pendiente', color: '#5b5b68' },
  { value: 'tengo', label: 'Tengo', color: '#3D8BFF' },
  { value: 'comprado', label: 'Comprado', color: '#1D9E75' }
]

export default function ListView() {
  const { id } = useParams()
  const listQ = useAsync(() => fetchList(id), [id])
  const itemsQ = useAsync(() => fetchListItems(id), [id])
  const [text, setText] = useState('')
  const [editingNote, setEditingNote] = useState(null)
  const [noteVal, setNoteVal] = useState('')

  async function add() {
    if (!text.trim()) return
    await createItem({ list_id: id, text: text.trim(), note: null })
    setText('')
    itemsQ.refetch()
  }

  async function toggle(item) {
    await updateItem(item.id, { checked: !item.checked })
    itemsQ.refetch()
  }

  async function setStatus(item, status) {
    await updateItem(item.id, { status })
    itemsQ.refetch()
  }

  async function remove(itemId) {
    await deleteItem(itemId)
    itemsQ.refetch()
  }

  async function saveNote(itemId) {
    await updateItem(itemId, { note: noteVal || null })
    setEditingNote(null)
    setNoteVal('')
    itemsQ.refetch()
  }

  const list = listQ.data
  const items = itemsQ.data || []

  return (
    <div>
      <div className="mb-4">
        <Link to="/listas" className="text-xs text-ink-400 hover:text-white">← Listas</Link>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold mt-1 flex items-center gap-2">
          <span>{list?.icon || '📝'}</span> {list?.name || 'Cargando…'}
        </h1>
      </div>

      <Card>
        <div className="flex gap-2 mb-3">
          <input
            className="input"
            placeholder="Agregar ítem…"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && add()}
          />
          <Button onClick={add}>+</Button>
        </div>

        {items.length === 0 ? (
          <p className="text-center text-sm text-ink-400 py-6">Lista vacía</p>
        ) : (
          <ul className="divide-y divide-white/[0.05]">
            {items.map((it) => {
              const statusObj = STATUSES.find((s) => s.value === it.status) || STATUSES[0]
              return (
                <li key={it.id} className="py-2.5 group">
                  <div className="flex items-start gap-3">
                    <button
                      onClick={() => toggle(it)}
                      className={`w-5 h-5 mt-0.5 rounded-md border-2 grid place-items-center shrink-0 transition ${
                        it.checked ? 'bg-teal-brand border-teal-brand' : 'border-white/15 hover:border-white/30'
                      }`}
                    >
                      {it.checked && <span className="text-white text-[10px]">✓</span>}
                    </button>
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm ${it.checked ? 'line-through text-ink-400' : ''}`}>{it.text}</div>
                      {editingNote === it.id ? (
                        <div className="mt-1.5 flex gap-2">
                          <input
                            autoFocus
                            className="input text-xs !py-1"
                            value={noteVal}
                            onChange={(e) => setNoteVal(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && saveNote(it.id)}
                            onBlur={() => saveNote(it.id)}
                          />
                        </div>
                      ) : it.note ? (
                        <button
                          onClick={() => { setEditingNote(it.id); setNoteVal(it.note) }}
                          className="text-[11px] text-ink-400 mt-0.5 hover:text-white text-left"
                        >
                          {it.note}
                        </button>
                      ) : (
                        <button
                          onClick={() => { setEditingNote(it.id); setNoteVal('') }}
                          className="text-[11px] text-ink-500 mt-0.5 opacity-0 group-hover:opacity-100 hover:text-white"
                        >+ nota</button>
                      )}
                    </div>
                    <select
                      value={it.status}
                      onChange={(e) => setStatus(it, e.target.value)}
                      className="bg-ink-800 border border-white/[0.06] rounded text-xs px-1.5 py-1"
                      style={{ color: statusObj.color }}
                    >
                      {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                    </select>
                    <button
                      onClick={() => remove(it.id)}
                      className="opacity-0 group-hover:opacity-100 text-ink-400 hover:text-coral-brand text-xs"
                    >✕</button>
                  </div>
                </li>
              )
            })}
          </ul>
        )}
      </Card>
    </div>
  )
}
