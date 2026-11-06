import { AnimatePresence, motion } from 'framer-motion'
import { differenceInCalendarDays, parseISO } from 'date-fns'
import { colorFor } from '../../../shared/lib/constants.js'
import { fmt } from '../../../shared/lib/dates.js'
import { hm, stageOf } from '../lib/tiempo.js'
import SkillPractices from './SkillPractices.jsx'
import SkillResources from './SkillResources.jsx'

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

              <SkillPractices skillId={skill.id} version={skill.total_minutes} onChanged={onChanged} />
              <SkillResources skill={skill} onChanged={onChanged} />

              <button onClick={onEdit} className="text-xs font-semibold text-ink-400 hover:text-ink-100">Editar skill</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </article>
  )
}
