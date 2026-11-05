import { useState } from 'react'
import Card from '../../../shared/components/ui/Card.jsx'
import Button from '../../../shared/components/ui/Button.jsx'
import BookModal from './BookModal.jsx'

const SHELVES = [
  { key: 'leyendo', label: 'Leyendo', tone: 'text-up' },
  { key: 'pendiente', label: 'Pendientes', tone: 'text-ink-300' },
  { key: 'leido', label: 'Leídos', tone: 'text-accent' }
]

// Los estantes y el conteo del año vienen agrupados del backend
export default function Books({ library, skills, onChange }) {
  const [editing, setEditing] = useState(null)
  const [adding, setAdding] = useState(false)
  const grouped = library.shelves
  const skillName = Object.fromEntries(skills.map((sk) => [sk.id, sk.name]))

  return (
    <Card
      title="Biblioteca"
      subtitle={<><span className="font-mono text-ink-100">{library.read_this_year}</span> leídos en {library.year}</>}
      action={<Button size="sm" onClick={() => setAdding(true)}>+ Libro</Button>}
    >
      <div className="space-y-5">
        {SHELVES.map((shelf) => (
          <div key={shelf.key}>
            <h4 className={`text-[11px] uppercase tracking-wider font-bold mb-2 ${shelf.tone}`}>
              {shelf.label} <span className="font-mono text-ink-400">· {grouped[shelf.key].length}</span>
            </h4>
            {grouped[shelf.key].length === 0 ? (
              <p className="text-xs text-ink-400">Vacío</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {grouped[shelf.key].map((b) => (
                  <button
                    key={b.id}
                    onClick={() => setEditing(b)}
                    className="text-left bg-ink-900 border border-ink-700 rounded-xl p-3 hover:border-ink-600 transition-colors"
                  >
                    <div className="text-sm font-medium leading-tight">{b.title}</div>
                    {b.author && <div className="text-xs text-ink-400 mt-0.5">{b.author}</div>}
                    <div className="flex items-center justify-between mt-1.5">
                      {b.rating ? (
                        <span className="text-xs text-warn" aria-label={`${b.rating} de 5`}>{'★'.repeat(b.rating)}<span className="text-ink-600">{'★'.repeat(5 - b.rating)}</span></span>
                      ) : <span />}
                      {b.skill_id && skillName[b.skill_id] && (
                        <span className="text-[9px] font-bold tracking-wider uppercase text-up truncate">{skillName[b.skill_id]}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      <BookModal
        open={adding || !!editing}
        onClose={() => { setAdding(false); setEditing(null) }}
        initial={editing}
        skills={skills}
        onSaved={() => { setAdding(false); setEditing(null); onChange() }}
        onDeleted={() => { setEditing(null); onChange() }}
      />
    </Card>
  )
}
