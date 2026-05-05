import { useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchLists, createList, deleteList } from './queries.js'

const ICONS = ['📝', '🛒', '🎬', '✈️', '🎁', '📚', '🎵', '🍳', '🏃', '💡']
const COLORS = ['#1D9E75', '#7F77DD', '#D85A30', '#3D8BFF', '#F4B400', '#E33E3E']

export default function ListsGrid() {
  const listsQ = useAsync(() => fetchLists(), [])
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ name: '', color: COLORS[0], icon: ICONS[0] })

  async function save() {
    if (!form.name.trim()) return
    await createList({ name: form.name.trim(), color: form.color, icon: form.icon })
    setForm({ name: '', color: COLORS[0], icon: ICONS[0] })
    setAdding(false)
    listsQ.refetch()
  }

  async function remove(id, e) {
    e.preventDefault()
    e.stopPropagation()
    if (!confirm('¿Eliminar lista y todos sus ítems?')) return
    await deleteList(id)
    listsQ.refetch()
  }

  if ((listsQ.data || []).length === 0) {
    return (
      <>
        <EmptyState
          icon="📋"
          title="Sin listas todavía"
          description="Creá tu primera lista para organizar lo que quieras."
          action={<Button onClick={() => setAdding(true)}>+ Nueva lista</Button>}
        />
        <NewListModal open={adding} onClose={() => setAdding(false)} form={form} setForm={setForm} onSave={save} />
      </>
    )
  }

  return (
    <>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {listsQ.data.map((list) => {
          const total = (list.list_items || []).length
          const done = (list.list_items || []).filter((it) => it.checked || it.status === 'comprado').length
          return (
            <Link
              to={`/listas/${list.id}`}
              key={list.id}
              className="card-pad block group hover:border-white/15 transition relative"
              style={{ borderLeft: `3px solid ${list.color}` }}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xl">{list.icon || '📝'}</span>
                  <h3 className="font-display font-semibold truncate">{list.name}</h3>
                </div>
                <button
                  onClick={(e) => remove(list.id, e)}
                  className="opacity-0 group-hover:opacity-100 text-ink-400 hover:text-coral-brand text-xs"
                >✕</button>
              </div>
              <div className="mt-2 text-xs text-ink-400">{done} / {total} completados</div>
              <div className="mt-2 h-1.5 bg-white/[0.05] rounded-full overflow-hidden">
                <div className="h-full transition-all" style={{ width: total ? `${(done / total) * 100}%` : '0%', backgroundColor: list.color }} />
              </div>
            </Link>
          )
        })}
        <button
          onClick={() => setAdding(true)}
          className="card-pad border-dashed text-ink-400 hover:text-white hover:border-white/15 transition grid place-items-center min-h-[120px]"
        >
          <div className="text-center">
            <div className="text-2xl mb-1">+</div>
            <div className="text-sm">Nueva lista</div>
          </div>
        </button>
      </div>
      <NewListModal open={adding} onClose={() => setAdding(false)} form={form} setForm={setForm} onSave={save} />
    </>
  )
}

function NewListModal({ open, onClose, form, setForm, onSave }) {
  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Nueva lista"
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="ghost" onClick={onClose}>Cancelar</Button>
          <Button onClick={onSave}>Crear</Button>
        </div>
      }
    >
      <div className="space-y-3">
        <div>
          <label className="label">Nombre</label>
          <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Compras, Películas, Viajes…" />
        </div>
        <div>
          <label className="label">Ícono</label>
          <div className="flex flex-wrap gap-2">
            {ICONS.map((i) => (
              <button
                type="button" key={i}
                onClick={() => setForm({ ...form, icon: i })}
                className={`w-10 h-10 rounded-lg text-xl grid place-items-center transition ${form.icon === i ? 'bg-white/[0.1] ring-1 ring-white/20' : 'bg-ink-800 hover:bg-ink-700'}`}
              >{i}</button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Color</label>
          <div className="flex gap-2">
            {COLORS.map((c) => (
              <button
                type="button" key={c}
                onClick={() => setForm({ ...form, color: c })}
                className={`w-7 h-7 rounded-full border-2 ${form.color === c ? 'border-white' : 'border-transparent'}`}
                style={{ backgroundColor: c }}
              />
            ))}
          </div>
        </div>
      </div>
    </Modal>
  )
}
