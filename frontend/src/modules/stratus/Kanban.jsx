import { useMemo, useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import Badge from '../../components/Badge.jsx'
import { PRIORITY_COLORS, STATUS_LABELS } from '../../lib/constants.js'
import { fmt } from '../../lib/dates.js'
import { createTask, updateTask, deleteTask } from './queries.js'

const COLUMNS = ['pendiente', 'en_progreso', 'hecho']

export default function Kanban({ tasks, projectFilter, onChange }) {
  const [adding, setAdding] = useState(null) // status when adding
  const [editing, setEditing] = useState(null)

  const filtered = useMemo(
    () => projectFilter === 'all' ? tasks : tasks.filter((t) => t.project === projectFilter),
    [tasks, projectFilter]
  )

  const grouped = useMemo(() => {
    const g = { pendiente: [], en_progreso: [], hecho: [] }
    filtered.forEach((t) => g[t.status]?.push(t))
    return g
  }, [filtered])

  async function onDragEnd(result) {
    const { destination, source, draggableId } = result
    if (!destination) return
    if (destination.droppableId === source.droppableId) return
    const newStatus = destination.droppableId
    const patch = { status: newStatus }
    if (newStatus === 'hecho') patch.completed_at = new Date().toISOString()
    else patch.completed_at = null
    await updateTask(draggableId, patch)
    onChange()
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {COLUMNS.map((col) => (
          <Droppable droppableId={col} key={col}>
            {(provided, snapshot) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className={`card-pad min-h-[200px] transition ${snapshot.isDraggingOver ? 'bg-ink-800' : ''}`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <h3 className="font-display font-semibold text-sm">{STATUS_LABELS[col]}</h3>
                    <span className="text-[11px] text-ink-400 px-1.5 py-0.5 rounded bg-white/[0.04]">
                      {grouped[col].length}
                    </span>
                  </div>
                  <button
                    onClick={() => setAdding(col)}
                    className="text-ink-400 hover:text-white text-sm w-6 h-6 grid place-items-center rounded hover:bg-white/[0.05]"
                  >+</button>
                </div>
                <div className="space-y-2">
                  {grouped[col].map((t, i) => (
                    <Draggable draggableId={t.id} index={i} key={t.id}>
                      {(p, snap) => (
                        <div
                          ref={p.innerRef}
                          {...p.draggableProps}
                          {...p.dragHandleProps}
                          onClick={() => setEditing(t)}
                          className={`bg-ink-800 border border-white/[0.05] rounded-lg p-3 cursor-pointer hover:border-white/15 transition ${snap.isDragging ? 'shadow-lg rotate-1' : ''}`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <div className="text-sm font-medium leading-tight">{t.title}</div>
                            <Badge color={PRIORITY_COLORS[t.priority] || '#5b5b68'}>{t.priority}</Badge>
                          </div>
                          <div className="flex items-center justify-between text-[11px] text-ink-400">
                            <span>{t.project || '—'}</span>
                            {t.due_date && <span>📅 {fmt(t.due_date, 'd MMM')}</span>}
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              </div>
            )}
          </Droppable>
        ))}
      </div>

      <TaskModal
        open={!!adding}
        onClose={() => setAdding(null)}
        initial={{ status: adding }}
        onSaved={() => { setAdding(null); onChange() }}
      />
      <TaskModal
        open={!!editing}
        onClose={() => setEditing(null)}
        initial={editing}
        onSaved={() => { setEditing(null); onChange() }}
        onDeleted={() => { setEditing(null); onChange() }}
      />
    </DragDropContext>
  )
}

function TaskModal({ open, onClose, initial, onSaved, onDeleted }) {
  const empty = { title: '', description: '', status: 'pendiente', priority: 'media', project: '', due_date: '' }
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    setForm({
      title: initial?.title || '',
      description: initial?.description || '',
      status: initial?.status || 'pendiente',
      priority: initial?.priority || 'media',
      project: initial?.project || '',
      due_date: initial?.due_date || ''
    })
  }, [open, initial?.id, initial?.status])

  function reset() { setForm(empty) }

  async function save() {
    if (!form.title.trim()) return
    const payload = {
      title: form.title.trim(),
      description: form.description || null,
      status: form.status,
      priority: form.priority,
      project: form.project.trim() || null,
      due_date: form.due_date || null
    }
    if (initial?.id) await updateTask(initial.id, payload)
    else await createTask(payload)
    reset()
    onSaved()
  }

  async function remove() {
    if (initial?.id) {
      await deleteTask(initial.id)
      reset()
      onDeleted?.()
    }
  }

  function close() {
    reset()
    onClose()
  }

  return (
    <Modal
      open={open}
      onClose={close}
      title={initial?.id ? 'Editar tarea' : 'Nueva tarea'}
      footer={
        <div className="flex justify-between gap-2">
          {initial?.id ? <Button variant="danger" size="sm" onClick={remove}>Eliminar</Button> : <span />}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={close}>Cancelar</Button>
            <Button onClick={save}>Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-3">
        <div>
          <label className="label">Título</label>
          <input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        </div>
        <div>
          <label className="label">Descripción</label>
          <textarea className="input min-h-[80px]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Prioridad</label>
            <select className="input" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
              <option value="alta">Alta</option>
              <option value="media">Media</option>
              <option value="baja">Baja</option>
            </select>
          </div>
          <div>
            <label className="label">Estado</label>
            <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="pendiente">Pendiente</option>
              <option value="en_progreso">En progreso</option>
              <option value="hecho">Hecho</option>
            </select>
          </div>
          <div>
            <label className="label">Proyecto</label>
            <input className="input" value={form.project} onChange={(e) => setForm({ ...form, project: e.target.value })} placeholder="Stratus web" />
          </div>
          <div>
            <label className="label">Fecha límite</label>
            <input type="date" className="input" value={form.due_date || ''} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
          </div>
        </div>
      </div>
    </Modal>
  )
}
