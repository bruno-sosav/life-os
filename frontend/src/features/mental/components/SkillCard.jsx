import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { differenceInCalendarDays, parseISO } from 'date-fns'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { colorFor } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { deletePractice, fetchPractices } from '../api/practicas.api.js'
import { createResource, deleteResource } from '../api/recursos.api.js'
import { hm, stageOf } from '../lib/tiempo.js'

const KINDS = ['curso', 'libro', 'link', 'video', 'otro']

function lastText(day) {
  if (!day) return { text: 'Sin prácticas todavía', stale: false }
  const days = differenceInCalendarDays(new Date(), parseISO(day))
  const text = days === 0 ? 'hoy' : days === 1 ? 'ayer' : `hace ${days} días`
  return { text: `Última: ${text}`, stale: days > 7 }
}

// Una skill: cerrada muestra la semana contra la meta; abierta, el historial y sus recursos
export default function SkillCard({ skill, open, onToggle, onEdit, onChanged }) {
  const stage = stageOf(skill.stage)
  const goal = skill.weekly_goal_min
  const share = goal ? Math.min(skill.week_minutes / goal, 1) : 0
  const last = lastText(skill.last_practice)
  const maxWeek = Math.max(1, ...skill.weeks.map((w) => w.minutes))

  return (
    <article className="card overflow-hidden transition-colors hover:border-ink-600">
      <button onClick={onToggle} aria-expanded={open} className="w-full text-left p-4 space-y-3">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="text-[15px] font-semibold truncate">{skill.name}</div>
            {skill.type && (
              <div className="text-[10px] font-bold tracking-wider uppercase mt-0.5" style={{ color: colorFor(skill.type) }}>{skill.type}</div>
            )}
          </div>
          <span className={`text-[10px] font-bold tracking-wider uppercase shrink-0 ${stage.tone}`}>{stage.label}</span>
        </div>
        {goal ? (
          <div className="space-y-1.5">
            <div className="h-1.5 bg-ink-700 rounded-full overflow-hidden" aria-hidden="true">
              <motion.div className="h-full rounded-full bg-up" initial={{ width: 0 }} animate={{ width: `${share * 100}%` }}
                transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }} />
            </div>
            <div className="flex justify-between text-[11px]">
              <span className="text-ink-400"><span className="font-mono text-ink-100">{hm(skill.week_minutes)}</span> de {hm(goal)} esta semana</span>
              <span className={last.stale ? 'text-warn' : 'text-ink-400'}>{last.text}</span>
            </div>
          </div>
        ) : (
          <div className="text-[11px] text-ink-400">
            <span className="font-mono text-ink-100">{hm(skill.week_minutes)}</span> esta semana · <span className={last.stale ? 'text-warn' : ''}>{last.text}</span>
          </div>
        )}
      </button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.22 }} className="overflow-hidden">
            <div className="border-t border-ink-700 p-4 space-y-4">
              <div className="flex items-baseline justify-between">
                <span className="text-xs text-ink-400">Total</span>
                <span className="font-mono text-sm font-bold">{hm(skill.total_minutes)}</span>
              </div>

              <div>
                <div className="label">Minutos por semana</div>
                <div role="img" aria-label="Minutos de las últimas 6 semanas" className="flex items-end gap-1.5 h-14">
                  {skill.weeks.map((w, i) => (
                    <div key={w.week_start} title={`Semana del ${fmt(w.week_start, 'd MMM')}: ${hm(w.minutes)}`}
                      className={`flex-1 rounded-t ${i === skill.weeks.length - 1 ? 'bg-up' : 'bg-ink-600'}`}
                      style={{ height: `${Math.max(4, (w.minutes / maxWeek) * 100)}%` }} />
                  ))}
                </div>
              </div>

              <Practices skillId={skill.id} version={skill.total_minutes} onChanged={onChanged} />
              <Resources skill={skill} onChanged={onChanged} />

              <button onClick={onEdit} className="text-xs font-semibold text-ink-400 hover:text-ink-100">Editar skill</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  )
}

function Practices({ skillId, version, onChanged }) {
  const practicesQ = useAsync(() => fetchPractices(skillId), [skillId, version])
  const practices = practicesQ.data || []

  async function remove(p) {
    if (!confirm(`¿Borrar la práctica de ${hm(p.minutes)}?`)) return
    try {
      await deletePractice(p.id)
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div>
      <div className="label">Últimas prácticas</div>
      {!practices.length ? <p className="text-xs text-ink-400">Todavía no registraste ninguna.</p> : (
        <ul className="space-y-1">
          {practices.map((p) => (
            <li key={p.id} className="flex items-center gap-3 text-sm">
              <span className="font-mono text-xs text-ink-400 w-12">{fmt(p.date, 'dd/MM')}</span>
              <span className="flex-1 min-w-0 truncate text-ink-300">{p.note || '—'}</span>
              <span className="font-mono font-semibold">{p.minutes}′</span>
              <button onClick={() => remove(p)} aria-label={`Borrar práctica de ${hm(p.minutes)}`}
                className="w-7 h-7 rounded-md grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs">✕</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function Resources({ skill, onChanged }) {
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
