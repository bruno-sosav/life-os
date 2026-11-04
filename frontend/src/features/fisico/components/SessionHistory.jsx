import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Card from '../../../shared/components/ui/Card.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { fmt } from '../../../shared/lib/dates.js'
import { item, list } from '../../../shared/lib/motion.js'
import { toast } from '../../../shared/store/toastStore.js'
import { deleteSession } from '../api/sesiones.api.js'
import { formatValue } from '../lib/campos.js'

// Todas las sesiones juntas, filtrables por tipo (y por día, desde el calendario)
export default function SessionHistory({ sessions, activities, colorOf, day, onClearDay, onDeleted }) {
  const [type, setType] = useState(null)
  const [open, setOpen] = useState(null)
  const byId = Object.fromEntries(activities.map((a) => [a.id, a]))
  const shown = sessions.filter((s) => (!type || s.activity_id === type) && (!day || s.date === day))
  const used = activities.filter((a) => sessions.some((s) => s.activity_id === a.id))

  async function remove(session) {
    if (!confirm('¿Borrar esta sesión?')) return
    try {
      await deleteSession(session.id)
      toast.success('Sesión borrada')
      onDeleted()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Card
      title="Historial"
      subtitle={day ? <>Solo el <span className="font-mono">{fmt(day, "d 'de' MMM")}</span> · <button onClick={onClearDay} className="text-up hover:underline">ver todo</button></> : null}
    >
      {used.length > 1 && (
        <div className="flex flex-wrap gap-1.5 mb-3" role="group" aria-label="Filtrar por tipo">
          {[{ id: null, name: 'Todos' }, ...used].map((a) => (
            <button key={a.id ?? 'todos'} onClick={() => setType(a.id)} aria-pressed={type === a.id}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                type === a.id ? 'bg-ink-700 text-ink-100' : 'text-ink-400 hover:text-ink-100'
              }`}>
              {a.id && <span className="w-1.5 h-1.5 rounded-full" style={{ background: colorOf(a.id) }} />}
              {a.name}
            </button>
          ))}
        </div>
      )}

      {!shown.length ? (
        <EmptyState icon="—" title="Sin entrenamientos" description={day ? 'Ese día no registraste nada.' : 'Registrá el primero con el botón de arriba.'} />
      ) : (
        <motion.ul key={`${type}-${day}`} variants={list} initial="hidden" animate="show" className="divide-y divide-ink-700">
          {shown.map((s) => {
            const activity = byId[s.activity_id]
            const values = (activity?.fields || [])
              .filter((f) => s.values[f.id] !== undefined)
              .map((f) => `${f.name}: ${formatValue(f, s.values[f.id])}`)
            const isOpen = open === s.id
            return (
              <motion.li key={s.id} variants={item}>
                <div className="flex items-center gap-3 py-3">
                  <button onClick={() => setOpen(isOpen ? null : s.id)} aria-expanded={isOpen}
                    className="flex-1 min-w-0 flex items-center gap-3 text-left">
                    <span className="w-1 self-stretch rounded-full" style={{ background: colorOf(s.activity_id) }} />
                    <span className="font-mono text-xs text-ink-400 w-14 shrink-0">{fmt(s.date, 'd MMM')}</span>
                    <span className="flex-1 min-w-0">
                      <span className="text-sm font-semibold">{activity?.name ?? 'Tipo borrado'}</span>
                      <span className="block text-xs text-ink-400 truncate">
                        {[s.exercises.length ? `${s.exercises.length} ejercicios` : null, ...values].filter(Boolean).join(' · ') || (s.attended ? 'Asistió' : 'Faltó')}
                      </span>
                    </span>
                    <span className={`text-ink-400 text-xs transition-transform ${isOpen ? 'rotate-180' : ''}`}>▾</span>
                  </button>
                  <button onClick={() => remove(s)} aria-label="Borrar sesión"
                    className="w-8 h-8 rounded-lg grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs">✕</button>
                </div>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }} className="overflow-hidden">
                      <div className="pb-3 pl-[4.5rem] space-y-1">
                        {s.exercises.map((e) => (
                          <div key={e.id} className="flex justify-between text-sm">
                            <span>{e.exercise_name}</span>
                            <span className="font-mono text-ink-300">
                              {e.sets ?? '—'}×{e.reps ?? '—'}{e.weight_kg != null ? ` · ${e.weight_kg} kg` : ''}
                            </span>
                          </div>
                        ))}
                        {s.notes && <p className="text-xs text-ink-400 pt-1">{s.notes}</p>}
                        {!s.exercises.length && !s.notes && <p className="text-xs text-ink-400">Sin detalle</p>}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.li>
            )
          })}
        </motion.ul>
      )}
    </Card>
  )
}
