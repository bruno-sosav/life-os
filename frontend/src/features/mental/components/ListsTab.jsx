import { useEffect, useState } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { AnimatePresence, motion } from 'framer-motion'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { swap } from '../../../shared/lib/motion.js'
import { toast } from '../../../shared/store/toastStore.js'
import { addItem, clearDone, deleteItem, itemToSkill, moveItem, updateItem } from '../api/listas.api.js'
import ListModal from './ListModal.jsx'
import ItemModal from './ItemModal.jsx'
import ListItemRow from './ListItemRow.jsx'

function PencilIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z" />
    </svg>
  )
}

// Listas libres para tachar. Las que son "para aprender" pasan sus ítems a Aprender.
export default function ListsTab({ lists, setLists, onChanged, onSkillCreated }) {
  const [selected, setSelected] = useState(null)
  const [editing, setEditing] = useState(null)
  const [draft, setDraft] = useState('')
  const [editingItem, setEditingItem] = useState(null)
  const current = lists.find((l) => l.id === selected) ?? lists[0]

  useEffect(() => { if (!selected && lists.length) setSelected(lists[0].id) }, [lists, selected])

  // La pantalla cambia al instante y se guarda atrás; si falla, vuelve a lo del backend
  function patchItems(fn) {
    setLists(lists.map((l) => (l.id === current.id ? { ...l, items: fn(l.items) } : l)))
  }
  async function persist(request) {
    try { await request } catch (e) { toast.error(e.message); onChanged() }
  }

  async function add() {
    const text = draft.trim()
    if (!text) return
    setDraft('')
    try {
      const created = await addItem(current.id, { text })
      patchItems((items) => [created, ...items])
    } catch (e) { toast.error(e.message) }
  }

  function toggle(it) {
    patchItems((items) => {
      const rest = items.filter((x) => x.id !== it.id)
      const flipped = { ...it, done: !it.done }
      // Al tacharlo baja con los hechos; al destacharlo vuelve arriba de los pendientes
      return flipped.done ? [...rest, flipped] : [flipped, ...rest]
    })
    persist(updateItem(it.id, { done: !it.done }))
  }

  function edit(it, patch) {
    patchItems((items) => items.map((x) => (x.id === it.id ? { ...x, ...patch } : x)))
    persist(updateItem(it.id, patch))
  }

  function remove(it) {
    patchItems((items) => items.filter((x) => x.id !== it.id))
    persist(deleteItem(it.id))
  }

  function clear() {
    patchItems((items) => items.filter((x) => !x.done))
    persist(clearDone(current.id))
  }

  async function learn(it) {
    try {
      await itemToSkill(it.id)
      toast.success(`${it.text} ahora está en Aprender`)
      onChanged()
      onSkillCreated()
    } catch (e) { toast.error(e.message) }
  }

  function onDragEnd({ source, destination }) {
    if (!destination || destination.index === source.index) return
    const pending = current.items.filter((i) => !i.done)
    const done = current.items.filter((i) => i.done)
    const [moved] = pending.splice(source.index, 1)
    pending.splice(destination.index, 0, moved)
    patchItems(() => [...pending, ...done])
    persist(moveItem(moved.id, destination.index))
  }

  const pending = current?.items.filter((i) => !i.done) ?? []
  const done = current?.items.filter((i) => i.done) ?? []

  return (
    <div className="space-y-3">
      <nav aria-label="Tus listas" className="flex items-center gap-1.5 overflow-x-auto no-scrollbar pb-1">
        {lists.map((l) => {
          const active = l.id === current?.id
          return (
            <button key={l.id} onClick={() => setSelected(l.id)} aria-current={active ? 'page' : undefined}
              className={`shrink-0 flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-semibold transition-colors ${
                active ? 'bg-ink-700 border-ink-600 text-ink-100' : 'border-ink-700 text-ink-400 hover:text-ink-100'
              }`}>
              <span className="w-2 h-2 rounded-full" style={{ background: l.color || '#8C948F' }} />
              {l.name}
              <span className="font-mono text-[11px] text-ink-400">{l.items.filter((i) => !i.done).length}</span>
            </button>
          )
        })}
        <button onClick={() => setEditing({})}
          className="shrink-0 px-3 py-2 rounded-lg border border-dashed border-ink-600 text-sm font-semibold text-ink-400 hover:text-up hover:border-up/40 transition">
          + Lista
        </button>
      </nav>

      {!current ? (
        <div className="card-pad">
          <EmptyState icon="+" title="Sin listas" description="Creá la primera: próximas compras, películas, cosas que querés aprender…" />
        </div>
      ) : (
        <AnimatePresence mode="wait">
          <motion.section key={current.id} {...swap} className="card">
            <header className="flex items-center justify-between px-4 pt-4 pb-2">
              <div className="flex items-center gap-2 min-w-0">
                <h3 className="font-semibold truncate">{current.name}</h3>
                {current.for_learning && <span className="text-[10px] font-bold tracking-wider uppercase text-up">Para aprender</span>}
                <button onClick={() => setEditing(current)} aria-label={`Editar ${current.name}`}
                  className="w-8 h-8 rounded-md grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700"><PencilIcon /></button>
              </div>
              <span className="text-xs text-ink-400"><span className="font-mono text-ink-100">{pending.length}</span> pendientes</span>
            </header>

            <div className="mx-4 mb-2 flex items-center gap-2 rounded-xl bg-ink-900 border border-ink-600 focus-within:border-accent px-3 transition-colors">
              <span className="text-up font-bold" aria-hidden="true">+</span>
              <input className="flex-1 bg-transparent py-3 text-sm focus:outline-none placeholder:text-ink-500"
                aria-label={`Agregar a ${current.name}`} placeholder="Agregar… (Enter)" maxLength={255}
                value={draft} onChange={(e) => setDraft(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()} />
            </div>

            <DragDropContext onDragEnd={onDragEnd}>
              <Droppable droppableId="pendientes">
                {(provided) => (
                  <ul ref={provided.innerRef} {...provided.droppableProps} className="px-2">
                    {pending.map((it, i) => (
                      <Draggable key={it.id} draggableId={it.id} index={i} disableInteractiveElementBlocking>
                        {(p, snap) => (
                          <li ref={p.innerRef} {...p.draggableProps} {...p.dragHandleProps}
                            style={snap.isDragging ? { ...p.draggableProps.style, boxShadow: '0 12px 24px rgba(0,0,0,0.5)' } : p.draggableProps.style}
                            className={`group flex items-center gap-3 px-2 py-2.5 rounded-lg ${snap.isDragging ? 'bg-ink-700' : 'hover:bg-ink-900'}`}>
                            <ListItemRow it={it} canLearn={current.for_learning} onToggle={toggle} onRemove={remove} onLearn={learn} onEdit={setEditingItem} />
                          </li>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </ul>
                )}
              </Droppable>
            </DragDropContext>

            {done.length > 0 && (
              <ul className="px-2">
                {done.map((it) => (
                  <li key={it.id} className="group flex items-center gap-3 px-2 py-2.5 rounded-lg hover:bg-ink-900">
                    <ListItemRow it={it} canLearn={false} onToggle={toggle} onRemove={remove} onLearn={learn} onEdit={setEditingItem} />
                  </li>
                ))}
              </ul>
            )}
            {!current.items.length && <p className="px-4 pb-4 text-sm text-ink-400">Lista vacía: escribí arriba y apretá Enter.</p>}

            <footer className="flex items-center justify-between border-t border-ink-700 px-4 py-2.5 mt-1">
              <span className="text-xs text-ink-400"><span className="font-mono">{done.length}</span> hechos</span>
              <button onClick={clear} disabled={!done.length}
                className="text-xs font-semibold text-ink-100 disabled:text-ink-500 hover:text-down px-1 py-1">Limpiar hechos</button>
            </footer>
          </motion.section>
        </AnimatePresence>
      )}

      <ItemModal item={editingItem} onClose={() => setEditingItem(null)} onSave={edit} />
      <ListModal list={editing} onClose={() => setEditing(null)}
        onSaved={(saved) => { onChanged(); setSelected(saved.id) }}
        onDeleted={() => { setSelected(null); onChanged() }} />
    </div>
  )
}
