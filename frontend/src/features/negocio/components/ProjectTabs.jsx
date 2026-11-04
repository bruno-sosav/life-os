import { useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { PICK_COLORS as COLORS } from '../../../shared/lib/constants.js'
import { createProject, deleteProject, updateProject } from '../api/proyectos.api.js'


function PencilIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 20h9" /><path d="M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z" />
    </svg>
  )
}

// Un tablero por proyecto: elegís cuál ves. El activo se puede renombrar o borrar.
export default function ProjectTabs({ projects, selected, onSelect, onCreated, onChanged, onDeleted }) {
  const [editing, setEditing] = useState(null) // null = cerrado, {} = nuevo, proyecto = editar
  const [form, setForm] = useState({ name: '', color: COLORS[0] })
  const isNew = !editing?.id

  function open(project) {
    setForm(project?.id ? { name: project.name, color: project.color || COLORS[0] } : { name: '', color: COLORS[0] })
    setEditing(project)
  }

  async function save() {
    if (!form.name.trim()) return toast.error('Ponele un nombre')
    try {
      if (isNew) {
        const project = await createProject({ name: form.name.trim(), color: form.color, emoji: null, description: null })
        toast.success('Proyecto creado')
        onCreated(project)
      } else {
        await updateProject(editing.id, { name: form.name.trim(), color: form.color })
        toast.success('Proyecto actualizado')
        onChanged()
      }
      setEditing(null)
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  async function remove() {
    if (!confirm(`¿Borrar "${editing.name}" y TODAS sus tareas? No se puede deshacer.`)) return
    try {
      await deleteProject(editing.id)
      toast.success('Proyecto borrado')
      setEditing(null)
      onDeleted(editing.id)
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <>
      <nav aria-label="Proyectos" className="flex items-center gap-1.5 overflow-x-auto no-scrollbar mb-4 pb-1">
        {projects.map((p) => {
          const active = p.id === selected
          return (
            <div key={p.id} className={`shrink-0 flex items-center rounded-lg border transition-colors ${
              active ? 'bg-ink-700 border-ink-600' : 'border-transparent hover:bg-ink-800'
            }`}>
              <button
                onClick={() => onSelect(p.id)}
                aria-current={active ? 'page' : undefined}
                className={`flex items-center gap-2 pl-3.5 py-2 text-sm font-semibold ${active ? 'text-ink-100 pr-1.5' : 'text-ink-400 hover:text-ink-100 pr-3.5'}`}
              >
                <span className="w-2 h-2 rounded-full" style={{ background: p.color || '#8C948F' }} />
                {p.name}
              </button>
              {active && (
                <button onClick={() => open(p)} aria-label={`Editar ${p.name}`}
                  className="w-8 h-8 mr-0.5 rounded-md grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-600 transition">
                  <PencilIcon />
                </button>
              )}
            </div>
          )
        })}
        <button
          onClick={() => open({})}
          className="shrink-0 px-3 py-2 rounded-lg text-sm font-semibold text-ink-400 hover:text-up hover:bg-ink-800 transition"
        >+ Proyecto</button>
      </nav>

      <Modal open={editing !== null} onClose={() => setEditing(null)} title={isNew ? 'Nuevo proyecto' : 'Editar proyecto'}
        footer={
          <div className="flex justify-between gap-2">
            {isNew ? <span /> : <Button variant="danger" size="sm" onClick={remove}>Borrar proyecto</Button>}
            <div className="flex gap-2">
              <Button variant="ghost" onClick={() => setEditing(null)}>Cancelar</Button>
              <Button onClick={save}>{isNew ? 'Crear' : 'Guardar'}</Button>
            </div>
          </div>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="label" htmlFor="project-name">Nombre</label>
            <input id="project-name" className="input" value={form.name} maxLength={255} autoFocus
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              onKeyDown={(e) => e.key === 'Enter' && save()} placeholder="Stratus Cuts, Facultad…" />
          </div>
          <div>
            <span className="label">Color</span>
            <div className="flex gap-2">
              {COLORS.map((c) => (
                <button key={c} type="button" aria-label={`Color ${c}`} aria-pressed={form.color === c}
                  onClick={() => setForm({ ...form, color: c })}
                  className={`w-8 h-8 rounded-full border-2 transition ${form.color === c ? 'border-ink-100 scale-110' : 'border-transparent'}`}
                  style={{ backgroundColor: c }} />
              ))}
            </div>
          </div>
        </div>
      </Modal>
    </>
  )
}
