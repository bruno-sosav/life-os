import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fmt } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
import { deletePractice, fetchPractices } from '../api/practicas.api.js'
import { hm } from '../lib/tiempo.js'

// Las últimas prácticas de una skill, con su ✕ para borrar
export default function SkillPractices({ skillId, version, onChanged }) {
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
