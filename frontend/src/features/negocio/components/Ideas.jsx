import { useState } from 'react'
import Card from '../../../shared/components/ui/Card.jsx'
import Button from '../../../shared/components/ui/Button.jsx'
import Modal from '../../../shared/components/ui/Modal.jsx'
import Badge from '../../../shared/components/ui/Badge.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fetchIdeas, createIdea, deleteIdea } from '../api/ideas.api.js'
import { fmt } from '../../../shared/lib/dates.js'
import { colorFor } from '../../../shared/lib/constants.js'
import { toast } from '../../../shared/store/toastStore.js'

export default function Ideas() {
  const ideasQ = useAsync(() => fetchIdeas(), [])
  const [adding, setAdding] = useState(false)
  const [expanded, setExpanded] = useState(null)
  const [form, setForm] = useState({ title: '', body: '', tags: '' })

  async function save() {
    if (!form.title.trim()) return
    try {
      await createIdea({
        title: form.title.trim(),
        body: form.body || null,
        tags: form.tags ? form.tags.split(',').map((t) => t.trim()).filter(Boolean) : null
      })
      toast.success('Idea guardada ✓')
      setForm({ title: '', body: '', tags: '' })
      setAdding(false)
      ideasQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Card title="Ideas" action={<Button size="sm" onClick={() => setAdding(true)}>+ Idea</Button>}>
      {!(ideasQ.data || []).length ? (
        <p className="text-sm text-ink-400 text-center py-6">Sin ideas todavía.</p>
      ) : (
        <ul className="divide-y divide-ink-700">
          {ideasQ.data.map((idea) => (
            <li key={idea.id} className="py-3 group">
              <button onClick={() => setExpanded(expanded === idea.id ? null : idea.id)} className="w-full text-left">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm font-semibold">{idea.title}</span>
                      {(idea.tags || []).map((t) => <Badge key={t} color={colorFor(t)}>#{t}</Badge>)}
                    </div>
                    <div className="text-[11px] text-ink-400 mt-0.5">{fmt(idea.created_at, "d MMM yyyy")}</div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button onClick={(e) => { e.stopPropagation(); deleteIdea(idea.id).then(() => { toast.success('Eliminada'); ideasQ.refetch() }) }}
                      className="opacity-0 group-hover:opacity-100 text-ink-500 hover:text-down text-xs">✕</button>
                    <span className="text-ink-500 text-xs">{expanded === idea.id ? '▲' : '▼'}</span>
                  </div>
                </div>
              </button>
              {expanded === idea.id && idea.body && (
                <p className="text-sm text-ink-300 mt-2 whitespace-pre-wrap">{idea.body}</p>
              )}
            </li>
          ))}
        </ul>
      )}
      <Modal open={adding} onClose={() => setAdding(false)} title="Nueva idea"
        footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => setAdding(false)}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
      >
        <div className="space-y-3">
          <div><label className="label">Título</label><input className="input" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></div>
          <div><label className="label">Desarrollo</label><textarea className="input min-h-[120px]" value={form.body} onChange={(e) => setForm({ ...form, body: e.target.value })} /></div>
          <div><label className="label">Tags (separados por coma)</label><input className="input" value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="producto, growth" /></div>
        </div>
      </Modal>
    </Card>
  )
}
