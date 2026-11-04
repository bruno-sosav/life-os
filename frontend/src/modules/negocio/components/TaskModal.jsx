import { useEffect, useState } from 'react'
import Button from '../../../components/Button.jsx'
import Modal from '../../../components/Modal.jsx'
import { PRIORITY_COLORS, STATUS_LABELS } from '../../../lib/constants.js'
import { toast } from '../../../store/toastStore.js'
import { createTask, deleteTask, updateTask } from '../api/tareas.api.js'

const blank = (status, projectId) => ({
  title: '', description: '', status: status || 'pendiente', priority: 'media', project_id: projectId, due_date: ''
})

// Crear (con `status` = la columna donde se tocó +) o editar (`task`)
export default function TaskModal({ open, task, status, projectId, projects, onClose, onSaved }) {
  const [form, setForm] = useState(blank(status, projectId))

  useEffect(() => {
    if (!open) return
    setForm(task
      ? { ...task, description: task.description || '', due_date: task.due_date || '' }
      : blank(status, projectId))
  }, [open, task, status, projectId])

  async function save() {
    if (!form.title.trim()) return toast.error('Ponele un título')
    const payload = {
      title: form.title.trim(),
      description: form.description || null,
      status: form.status,
      priority: form.priority,
      project_id: form.project_id,
      due_date: form.due_date || null
    }
    try {
      if (task) await updateTask(task.id, payload)
      else await createTask(payload)
      toast.success(task ? 'Tarea actualizada' : 'Tarea creada')
      onSaved()
    } catch (e) { toast.error(e.message) }
  }

  async function remove() {
    if (!confirm(`¿Borrar "${task.title}"?`)) return
    try {
      await deleteTask(task.id)
      toast.success('Tarea borrada')
      onSaved()
    } catch (e) { toast.error(e.message) }
  }

  const set = (patch) => setForm({ ...form, ...patch })

  return (
    <Modal open={open} onClose={onClose} title={task ? 'Editar tarea' : 'Nueva tarea'}
      footer={
        <div className="flex justify-between gap-2">
          {task ? <Button variant="danger" size="sm" onClick={remove}>Borrar</Button> : <span />}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancelar</Button>
            <Button onClick={save}>Guardar</Button>
          </div>
        </div>
      }
    >
      <div className="space-y-3">
        <div>
          <label className="label" htmlFor="task-title">Título</label>
          <input id="task-title" className="input" value={form.title} onChange={(e) => set({ title: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && save()} autoFocus />
        </div>
        <div>
          <label className="label" htmlFor="task-description">Descripción</label>
          <textarea id="task-description" className="input min-h-[80px]" value={form.description}
            onChange={(e) => set({ description: e.target.value })} />
        </div>
        <div>
          <span className="label">Prioridad</span>
          <div className="flex gap-1.5">
            {Object.keys(PRIORITY_COLORS).map((p) => (
              <button key={p} type="button" aria-pressed={form.priority === p} onClick={() => set({ priority: p })}
                className={`flex-1 py-2 rounded-lg border text-xs font-bold uppercase tracking-wider transition ${
                  form.priority === p ? 'bg-ink-700 border-ink-600' : 'border-ink-700 text-ink-400'
                }`}
                style={form.priority === p ? { color: PRIORITY_COLORS[p] } : {}}
              >{p}</button>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label" htmlFor="task-status">Columna</label>
            <select id="task-status" className="input" value={form.status} onChange={(e) => set({ status: e.target.value })}>
              {Object.entries(STATUS_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="task-due">Vence</label>
            <input id="task-due" type="date" className="input" value={form.due_date} onChange={(e) => set({ due_date: e.target.value })} />
          </div>
        </div>
        {task && projects.length > 1 && (
          <div>
            <label className="label" htmlFor="task-project">Proyecto</label>
            <select id="task-project" className="input" value={form.project_id} onChange={(e) => set({ project_id: e.target.value })}>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
          </div>
        )}
      </div>
    </Modal>
  )
}
