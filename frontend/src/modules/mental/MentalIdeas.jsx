import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import Badge from '../../components/Badge.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchMentalIdeas, fetchIdeaTags, createMentalIdea, deleteMentalIdea } from './queries.js'
import { fmt } from '../../lib/dates.js'
import { toast } from '../../store/toastStore.js'

const COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#5AC8FA', '#FF453A', '#FFD60A']
const DEFAULT_TAG = '💡 Idea'

// Las etiquetas son libres: cada una toma siempre el mismo color a partir de su texto
function tagColor(tag) {
  let hash = 0
  for (const ch of tag) hash = (hash * 31 + ch.codePointAt(0)) >>> 0
  return COLORS[hash % COLORS.length]
}

export default function MentalIdeas() {
  const [filter, setFilter] = useState(null)
  const ideasQ = useAsync(() => fetchMentalIdeas(filter), [filter])
  const tagsQ = useAsync(() => fetchIdeaTags(), [])
  const [adding, setAdding] = useState(false)
  const [form, setForm] = useState({ text: '', author: '', tag: DEFAULT_TAG })
  const tags = (tagsQ.data || []).map((t) => t.tag)
  const ideas = ideasQ.data || []

  async function save() {
    if (!form.text.trim()) return
    try {
      await createMentalIdea({ text: form.text.trim(), author: form.author.trim() || null, tag: form.tag.trim() || DEFAULT_TAG })
      toast.success('Guardada ✓')
      setForm({ text: '', author: '', tag: DEFAULT_TAG })
      setAdding(false)
      ideasQ.refetch()
      tagsQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  async function remove(id) {
    await deleteMentalIdea(id)
    toast.success('Eliminada')
    ideasQ.refetch()
    tagsQ.refetch()
  }

  return (
    <div>
      {/* Tag filter */}
      <div className="flex gap-1.5 mb-4 flex-wrap">
        <button
          onClick={() => setFilter(null)}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${!filter ? 'bg-white/[0.14] text-white' : 'text-white/35 hover:text-white'}`}
        >Todas</button>
        {(tagsQ.data || []).map(({ tag, count }) => {
          const color = tagColor(tag)
          return (
            <button
              key={tag}
              aria-pressed={filter === tag}
              onClick={() => setFilter(filter === tag ? null : tag)}
              className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${filter === tag ? 'text-white' : 'text-white/35 hover:text-white'}`}
              style={filter === tag ? { background: `${color}33`, border: `1px solid ${color}50`, color } : { background: 'rgba(255,255,255,0.06)' }}
            >{tag} <span className="opacity-60">· {count}</span></button>
          )
        })}
      </div>

      <Card
        title="Frases & Ideas"
       
        action={<Button size="sm" color="purple" onClick={() => setAdding(true)}>+ Nueva</Button>}
      >
        {!ideas.length ? (
          <EmptyState icon="💡" title="Sin ideas" description="Guardá frases, ideas y aprendizajes." />
        ) : (
          <ul className="divide-y divide-white/[0.04]">
            {ideas.map((idea) => {
              return (
                <li key={idea.id} className="py-3 group flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium leading-snug">"{idea.text}"</p>
                    {idea.author && <p className="text-xs text-white/35 mt-0.5">— {idea.author}</p>}
                    <div className="flex items-center gap-2 mt-1.5">
                      <Badge color={tagColor(idea.tag)}>{idea.tag}</Badge>
                      <span className="text-[11px] text-white/25">{fmt(idea.created_at, 'd MMM')}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => remove(idea.id)}
                    aria-label="Eliminar idea"
                    className="opacity-0 group-hover:opacity-100 focus:opacity-100 text-white/25 hover:text-[#FF453A] text-xs shrink-0 mt-0.5"
                  >✕</button>
                </li>
              )
            })}
          </ul>
        )}
      </Card>

      <Modal open={adding} onClose={() => setAdding(false)} title="Nueva frase o idea"
        footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={() => setAdding(false)}>Cancelar</Button><Button onClick={save} color="purple">Guardar</Button></div>}
      >
        <div className="space-y-3">
          <div><label className="label">Texto</label><textarea className="input min-h-[100px]" value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} placeholder='"La disciplina es hacer lo que tenés que hacer..."' /></div>
          <div><label className="label">Autor (opcional)</label><input className="input" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} placeholder="Nombre del autor" /></div>
          <div>
            <label className="label" htmlFor="idea-tag">Etiqueta</label>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {tags.map((tag) => {
                  const color = tagColor(tag)
                  return (
                    <button key={tag} type="button" aria-pressed={form.tag === tag} onClick={() => setForm({ ...form, tag })}
                      className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold transition ${form.tag === tag ? 'text-white' : 'bg-white/[0.06] text-white/40'}`}
                      style={form.tag === tag ? { background: `${color}33`, border: `1px solid ${color}50`, color } : {}}
                    >{tag}</button>
                  )
                })}
              </div>
            )}
            <input id="idea-tag" className="input" value={form.tag} maxLength={30}
              onChange={(e) => setForm({ ...form, tag: e.target.value })} placeholder="Elegí una o escribí una nueva: 🎬 Película" />
          </div>
        </div>
      </Modal>
    </div>
  )
}
