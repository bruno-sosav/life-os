import { useState } from 'react'
import Button from '../../../shared/components/ui/Button.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { toast } from '../../../shared/store/toastStore.js'
import { updateActivity } from '../api/actividades.api.js'
import ActivityModal from './ActivityModal.jsx'

export default function Actividades({ activities, onChanged }) {
  const [editing, setEditing] = useState(null) // null = cerrado, {} = nueva, actividad = editar

  async function toggleActive(activity) {
    try {
      await updateActivity(activity.id, { active: !activity.active })
      toast.success(activity.active ? `${activity.name} en pausa` : `${activity.name} activa de nuevo`)
      onChanged()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <div>
      <div className="flex items-center justify-between gap-3 mb-3">
        <p className="text-xs text-ink-400">Pausá los que no estés haciendo: su historial queda guardado</p>
        <Button size="sm" onClick={() => setEditing({})}>+ Tipo</Button>
      </div>
      {!activities.length ? (
        <EmptyState icon="+" title="Sin tipos" description="Creá el primero: gym, calistenia, correr…" />
      ) : (
        <ul className="divide-y divide-ink-700">
          {activities.map((a) => {
            const fields = a.fields.filter((f) => !f.archived)
            return (
              <li key={a.id} className="py-3 flex items-center gap-3">
                <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: a.color || '#8C948F' }} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold flex items-center gap-2">
                    {a.name}
                    {!a.active && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-ink-600 text-ink-400">PAUSADA</span>}
                  </div>
                  <div className="text-xs text-ink-400 truncate">
                    {fields.length ? fields.map((f) => f.name).join(' · ') : 'Solo asistencia'}
                  </div>
                </div>
                <Button variant="ghost" size="sm" onClick={() => toggleActive(a)}>{a.active ? 'Pausar' : 'Reactivar'}</Button>
                <Button variant="secondary" size="sm" onClick={() => setEditing(a)}>Editar</Button>
              </li>
            )
          })}
        </ul>
      )}

      <ActivityModal
        initial={editing}
        onClose={() => setEditing(null)}
        onSaved={onChanged}
      />
    </div>
  )
}
