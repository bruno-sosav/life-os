import { useMemo, useState, useEffect } from 'react'
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import Badge from '../../components/Badge.jsx'
import { PRIORITY_COLORS, STATUS_LABELS } from '../../lib/constants.js'
import { fmt } from '../../lib/dates.js'
import { createTask, updateTask, deleteTask } from './queries.js'
import { toast } from '../../store/toastStore.js'

const COLUMNS = ['pendiente', 'en_progreso', 'hecho']
const COL_COLORS = { pendiente: '#ffffff22', en_progreso: '#FF9F0A', hecho: '#30D158' }

export default function Kanban({ tasks, projects, projectFilter, onChange }) {
  const [modal, setModal] = useState({ open: false, initial: null, status: null })

  const filtered = useMemo(
    () => projectFilter ? tasks.filter((t) => t.project_id === projectFilter) : tasks,
    [tasks, projectFilter]
  )
  const grouped = useMemo(() => {
    const g = { pendiente: [], en_progreso: [], hecho: [] }
    filtered.forEach((t) => g[t.status]?.push(t))
    return g
  }, [filtered])

  async function onDragEnd({ destination, source, draggableId }) {
    if (!destination || destination.droppableId === source.droppableId) return
    const newStatus = destination.droppableId
    try {
      await updateTask(draggableId, { status: newStatus, completed_at: newStatus === 'hecho' ? new Date().toISOString() : null })
      toast.success(`Movida a "${STATUS_LABELS[newStatus]}"`)
      onChange()
    } catch (e) { toast.error(e.message) }
  }

  async function quickDone(task) {
    const newStatus = task.status === 'hecho' ? 'pendiente' : 'hecho'
    try {
      await updateTask(task.id, { status: newStatus, completed_at: newStatus === 'hecho' ? new Date().toISOString() : null })
      toast.success(newStatus === 'hecho' ? '¡Tarea completada! ✓' : 'Movida a pendiente')
      onChange()
    } catch (e) { toast.error(e.message) }
  }

  const projectById = useMemo(() => {
    const m = {}
    projects.forEach((p) => { m[p.id] = p })
    return m
  }, [projects])

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {COLUMNS.map((col) => (
          <Droppable droppableId={col} key={col}>
            {(provided, snap) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="card-pad min-h-[160px] transition-colors"
                style={snap.isDraggingOver ? { background: 'rgba(255,255,255,0.08)' } : {}}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ background: COL_COLORS[col] }} />
                    <h3 className="font-display font-bold text-sm">{STATUS_LABELS[col]}</h3>
                    <span className="text-[11px] text-white/30 px-1.5 py-0.5 rounded-md bg-white/[0.05]">{grouped[col].length}</span>
                  </div>
                  <button
                    onClick={() => setModal({ open: true, initial: null, status: col })}
                    className="w-6 h-6 rounded-lg bg-white/[0.06] hover:bg-white/[0.12] grid place-items-center text-white/40 hover:text-white transition text-sm"
                  >+</button>
                </div>
                <div className="space-y-2">
                  {grouped[col].map((t, i) => {
                    const proj = projectById[t.project_id]
                    return (
                      <Draggable draggableId={t.id} index={i} key={t.id}>
                        {(p, snap) => (
                          <div
                            ref={p.innerRef}
                            {...p.draggableProps}
                            {...p.dragHandleProps}
                            className="rounded-[14px] p-3 transition-all"
                            style={{
                              background: snap.isDragging ? 'rgba(255,255,255,0.1)' : 'rgba(255,255,255,0.05)',
                              border: '1px solid rgba(255,255,255,0.07)',
                              transform: snap.isDragging ? `${p.draggableProps.style?.transform} rotate(2deg)` : undefined,
                              ...(p.draggableProps.style || {})
                            }}
                          >
                            <div className="flex items-start gap-2">
                              {/* Quick done checkbox */}
                              <button
                                onClick={() => quickDone(t)}
                                className="mt-0.5 w-5 h-5 rounded-full border-2 grid place-items-center shrink-0 transition-all ios-checkbox"
                                style={t.status === 'hecho'
                                  ? { background: '#30D158', borderColor: '#30D158' }
                                  : { borderColor: 'rgba(255,255,255,0.2)' }}
                              >
                                {t.status === 'hecho' && <span className="text-white text-[9px] font-bold">✓</span>}
                              </button>
                              <div className="flex-1 min-w-0">
                                <button
                                  onClick={() => setModal({ open: true, initial: t, status: null })}
                                  className="w-full text-left"
                                >
                                  <div className={`text-sm font-semibold leading-tight ${t.status === 'hecho' ? 'line-through text-white/30' : ''}`}>{t.title}</div>
                                  <div className="flex items-center gap-1.5 mt-1.5 flex-wrap">
                                    <Badge color={PRIORITY_COLORS[t.priority]}>{t.priority}</Badge>
                                    {proj && <Badge color={proj.color}>{proj.emoji} {proj.name}</Badge>}
                                    {t.due_date && <span className="text-[10px] text-white/30">📅 {fmt(t.due_date, 'd MMM')}</span>}
                                  </div>
                                </button>
                              </div>
                            </div>
                          </div>
                        )}
                      </Draggable>
                    )
                  })}
                  {provided.placeholder}
                </div>
              </div>
            )}
          </Droppable>
        ))}
      </div>

      <TaskModal
        open={modal.open}
        onClose={() => setModal({ open: false, initial: null, status: null })}
        initial={modal.initial}
        defaultStatus={modal.status}
        projects={projects}
        onSaved={() => { setModal({ open: false, initial: null, status: null }); onChange() }}
        onDeleted={() => { setModal({ open: false, initial: null, status: null }); onChange() }}
      />
    </DragDropContext>
  )
}

function TaskModal({ open, onClose, initial, defaultStatus, projects, onSaved, onDeleted }) {
  const empty = { title: '', description: '', status: defaultStatus || 'pendiente', priority: 'media', project_id: '', due_date: '' }
  const [form, setForm] = useState(empty)

  useEffect(() => {
    if (!open) return
    setForm({
      title: initial?.title || '',
      description: initial?.description || '',
      status: initial?.status || defaultStatus || 'pendiente',
      priority: initial?.priority || 'media',
      project_id: initial?.project_id || '',
      due_date: initial?.due_date || ''
    })
  }, [open, initial?.id, defaultStatus])

  async function save() {
    if (!form.title.trim()) return
    const payload = {
      title: form.title.trim(),
      description: form.description || null,
      status: form.status,
      priority: form.priority,
      project_id: form.project_id || null,
      due_date: form.due_date || null
    }
    try {
      if (initial?.id) await updateTask(initial.id, payload)
      else await createTask(payload)
      toast.success(initial?.id ? 'Tarea actualizada ✓' : 'Tarea creada ✓')
      onSaved()
    } catch (e) { toast.error(e.message) }
  }

  async function remove() {
    if (!initial?.id) return
    try {
      await deleteTask(initial.id)
      toast.success('Tarea eliminada')
      onDeleted()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title={initial?.id ? 'Editar tarea' : 'Nueva tarea'}
      footer={
        <div className="flex justify-between gap-2">
          {initial?.id ? <Button variant="danger" size="sm" onClick={remove}>Eliminar</Button> : <span />}
          <div className="flex gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>
        </div>
      }
    >
      <div className="space-y-3">
        <div><label className="label">Título</label><input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
        <div><label className="label">Descripción</label><textarea className="input min-h-[80px]" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Prioridad</label>
            <select className="input" value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value })}>
              <option value="alta">Alta</option><option value="media">Media</option><option value="baja">Baja</option>
            </select>
          </div>
          <div>
            <label className="label">Estado</label>
            <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              <option value="pendiente">Pendiente</option><option value="en_progreso">En progreso</option><option value="hecho">Hecho</option>
            </select>
          </div>
          <div>
            <label className="label">Proyecto</label>
            <select className="input" value={form.project_id} onChange={(e) => setForm({ ...form, project_id: e.target.value })}>
              <option value="">Sin proyecto</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.emoji} {p.name}</option>)}
            </select>
          </div>
          <div><label className="label">Fecha límite</label><input type="date" className="input" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} /></div>
        </div>
      </div>
    </Modal>
  )
}
