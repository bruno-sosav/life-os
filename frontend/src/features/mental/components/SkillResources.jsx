import { useState } from 'react'
import { toast } from '../../../shared/store/toastStore.js'
import { createResource, deleteResource } from '../api/recursos.api.js'

const KINDS = ['curso', 'libro', 'link', 'video', 'otro']

// Cursos, libros, links o videos de una skill; se agregan en línea
export default function SkillResources({ skill, onChanged }) {
  const [draft, setDraft] = useState(null) // null = cerrado

  async function add() {
    if (!draft.name.trim()) return
    try {
      await createResource(skill.id, { kind: draft.kind, name: draft.name.trim(), url: draft.url.trim() || null })
      setDraft(null)
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  async function remove(r) {
    try {
      await deleteResource(r.id)
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div>
      <div className="label">Recursos</div>
      <ul className="space-y-1">
        {skill.resources.map((r) => (
          <li key={r.id} className="flex items-center gap-3 text-sm">
            <span className="text-[9px] font-bold tracking-wider uppercase w-12" style={{ color: '#3987E5' }}>{r.kind}</span>
            {r.url
              ? <a href={r.url} target="_blank" rel="noreferrer" className="flex-1 min-w-0 truncate text-ink-300 hover:text-ink-100 underline underline-offset-2 decoration-ink-600">{r.name}</a>
              : <span className="flex-1 min-w-0 truncate text-ink-300">{r.name}</span>}
            <button onClick={() => remove(r)} aria-label={`Quitar ${r.name}`}
              className="w-7 h-7 rounded-md grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs">✕</button>
          </li>
        ))}
      </ul>
      {!skill.resources.length && !draft && (
        <p className="text-xs text-ink-400">Sin recursos: cursos, libros, links o videos.</p>
      )}
      {draft ? (
        <div className="mt-2 space-y-2">
          <div className="flex gap-1.5">
            {KINDS.map((k) => (
              <button key={k} type="button" aria-pressed={draft.kind === k} onClick={() => setDraft({ ...draft, kind: k })}
                className={`px-2.5 py-1 rounded-md border text-[11px] font-semibold uppercase tracking-wider ${
                  draft.kind === k ? 'bg-ink-700 border-ink-600 text-ink-100' : 'border-ink-700 text-ink-400'
                }`}>{k}</button>
            ))}
          </div>
          <input className="input !py-2 text-sm" aria-label="Nombre del recurso" placeholder="Nombre: Duolingo, un libro, un curso…" autoFocus
            value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} />
          <input className="input !py-2 text-sm" aria-label="Link (opcional)" placeholder="https://… (opcional)"
            value={draft.url} onChange={(e) => setDraft({ ...draft, url: e.target.value })}
            onKeyDown={(e) => e.key === 'Enter' && add()} />
          <div className="flex gap-2 justify-end">
            <button onClick={() => setDraft(null)} className="text-xs text-ink-400 hover:text-ink-100 px-2 py-1">Cancelar</button>
            <button onClick={add} className="text-xs font-semibold text-up hover:underline px-2 py-1">Agregar</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setDraft({ kind: 'link', name: '', url: '' })} className="mt-2 text-xs font-semibold text-up hover:underline">+ Recurso</button>
      )}
    </div>
  )
}
