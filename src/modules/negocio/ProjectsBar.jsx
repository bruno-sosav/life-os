import { useState } from 'react'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import { createProject, deleteProject } from './queries.js'
import { toast } from '../../store/toastStore.js'

const EMOJIS = ['📁', '🚀', '💼', '🌐', '🏢', '📱', '⚡', '🎯', '💡', '🛠']
const COLORS = ['#0A84FF', '#30D158', '#BF5AF2', '#FF9F0A', '#FF453A', '#5AC8FA']

export default function ProjectsBar({ projects, selected, onSelect, onRefetch }) {
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ name: '', emoji: '📁', color: '#0A84FF', description: '' })

  async function save() {
    if (!form.name.trim()) return
    try {
      await createProject({ name: form.name.trim(), emoji: form.emoji, color: form.color, description: form.description || null })
      toast.success('Proyecto creado ✓')
      setForm({ name: '', emoji: '📁', color: '#0A84FF', description: '' })
      setAdding(false)
      onRefetch()
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  return (
    <>
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar mb-4" style={{ scrollbarWidth: 'none' }}>
        <button
          onClick={() => onSelect(null)}
          className={`shrink-0 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
            !selected ? 'text-white shadow' : 'text-white/45 hover:text-white'
          }`}
          style={!selected ? { background: '#0A84FF' } : { background: 'rgba(255,255,255,0.07)' }}
        >
          Todos
        </button>
        {projects.map((p) => (
          <button
            key={p.id}
            onClick={() => onSelect(p.id === selected ? null : p.id)}
            className={`shrink-0 flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-semibold transition-all ${
              p.id === selected ? 'text-white shadow' : 'text-white/45 hover:text-white'
            }`}
            style={p.id === selected
              ? { background: p.color }
              : { background: 'rgba(255,255,255,0.07)' }}
          >
            <span>{p.emoji}</span>
            <span>{p.name}</span>
          </button>
        ))}
        <button
          onClick={() => setAdding(true)}
          className="shrink-0 px-3 py-2 rounded-full text-sm font-semibold text-white/30 hover:text-white hover:bg-white/[0.07] transition"
        >+ Proyecto</button>
      </div>

      <Modal
        open={adding} onClose={() => setAdding(false)} title="Nuevo proyecto"
        footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => setAdding(false)}>Cancelar</Button><Button onClick={save} color="blue">Crear</Button></div>}
      >
        <div className="space-y-3">
          <div><label className="label">Nombre</label><input autoFocus className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="Mi proyecto" /></div>
          <div>
            <label className="label">Emoji</label>
            <div className="flex gap-1.5 flex-wrap">
              {EMOJIS.map((e) => (
                <button key={e} type="button" onClick={() => setForm({ ...form, emoji: e })}
                  className={`w-9 h-9 rounded-lg text-lg grid place-items-center ${form.emoji === e ? 'bg-white/[0.15] ring-1 ring-white/20' : 'bg-white/[0.05]'}`}>
                  {e}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="label">Color</label>
            <div className="flex gap-2">
              {COLORS.map((c) => (
                <button key={c} type="button" onClick={() => setForm({ ...form, color: c })}
                  className={`w-8 h-8 rounded-full border-2 transition ${form.color === c ? 'border-white scale-110' : 'border-transparent'}`}
                  style={{ backgroundColor: c }} />
              ))}
            </div>
          </div>
          <div><label className="label">Descripción (opcional)</label><input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
        </div>
      </Modal>
    </>
  )
}
