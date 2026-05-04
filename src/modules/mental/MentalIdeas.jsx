import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import Badge from '../../components/Badge.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchMentalIdeas, createMentalIdea, deleteMentalIdea } from './queries.js'
import { fmt } from '../../lib/dates.js'
import { toast } from '../../store/toastStore.js'

const TAGS = [
  { value: 'frase', label: '💬 Frase', color: '#0A84FF' },
  { value: 'idea de negocio', label: '💼 Negocio', color: '#FF9F0A' },
  { value: 'aprendizaje', label: '📚 Aprendizaje', color: '#30D158' },
  { value: 'meta', label: '🎯 Meta', color: '#BF5AF2' },
  { value: 'idea', label: '💡 Idea', color: '#5AC8FA' }
]

export default function MentalIdeas() {
  const ideasQ = useAsync(() => fetchMentalIdeas(), [])
  const [adding, setAdding] = useState(false)
  const [filter, setFilter] = useState(null)
  const [form, setForm] = useState({ text: '', author: '', tag: 'idea' })

  const filtered = filter
    ? (ideasQ.data || []).filter((i) => i.tag === filter)
    : (ideasQ.data || [])

  async function save() {
    if (!form.text.trim()) return
    try {
      await createMentalIdea({ text: form.text.trim(), author: form.author.trim() || null, tag: form.tag })
      toast.success('Guardada ✓')
      setForm({ text: '', author: '', tag: 'idea' })
      setAdding(false)
      ideasQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div>
      {/* Tag filter */}
      <div className="flex gap-1.5 mb-4 flex-wrap">
        <button
          onClick={() => setFilter(null)}
          className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${!filter ? 'bg-white/[0.14] text-white' : 'text-white/35 hover:text-white'}`}
        >Todas</button>
        {TAGS.map((t) => (
          <button
            key={t.value}
            onClick={() => setFilter(filter === t.value ? null : t.value)}
            className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${filter === t.value ? 'text-white' : 'text-white/35 hover:text-white'}`}
            style={filter === t.value ? { background: `${t.color}33`, border: `1px solid ${t.color}50`, color: t.color } : { background: 'rgba(255,255,255,0.06)' }}
          >{t.label}</button>
        ))}
      </div>

      <Card
        title="Frases & Ideas"
        emoji="💡"
        action={<Button size="sm" color="purple" onClick={() => setAdding(true)}>+ Nueva</Button>}
      >
        {!filtered.length ? (
          <EmptyState icon="💡" title="Sin ideas" description="Guardá frases, ideas y aprendizajes." />
        ) : (
          <ul className="divide-y divide-white/[0.04]">
            {filtered.map((idea) => {
              const tagInfo = TAGS.find((t) => t.value === idea.tag)
              return (
                <li key={idea.id} className="py-3 group flex items-start gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium leading-snug">"{idea.text}"</p>
                    {idea.author && <p className="text-xs text-white/35 mt-0.5">— {idea.author}</p>}
                    <div className="flex items-center gap-2 mt-1.5">
                      {tagInfo && <Badge color={tagInfo.color}>{tagInfo.label}</Badge>}
                      <span className="text-[11px] text-white/25">{fmt(idea.created_at, 'd MMM')}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteMentalIdea(idea.id).then(() => { toast.success('Eliminada'); ideasQ.refetch() })}
                    className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs shrink-0 mt-0.5"
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
          <div><label className="label">Texto</label><textarea autoFocus className="input min-h-[100px]" value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} placeholder='"La disciplina es hacer lo que tenés que hacer..."' /></div>
          <div><label className="label">Autor (opcional)</label><input className="input" value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} placeholder="Nombre del autor" /></div>
          <div>
            <label className="label">Tipo</label>
            <div className="grid grid-cols-3 gap-1.5">
              {TAGS.map((t) => (
                <button key={t.value} type="button" onClick={() => setForm({ ...form, tag: t.value })}
                  className={`py-2 rounded-xl text-xs font-semibold transition ${form.tag === t.value ? 'text-white' : 'bg-white/[0.06] text-white/40'}`}
                  style={form.tag === t.value ? { background: `${t.color}33`, border: `1px solid ${t.color}50`, color: t.color } : {}}
                >{t.label}</button>
              ))}
            </div>
          </div>
        </div>
      </Modal>
    </div>
  )
}
