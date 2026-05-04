import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchJournalEntries, createJournalEntry, deleteJournalEntry } from './queries.js'
import { fmt, todayISO } from '../../lib/dates.js'
import { toast } from '../../store/toastStore.js'

const MOOD_EMOJIS = ['😔', '😐', '🙂', '😊', '🔥']

export default function Journal() {
  const entriesQ = useAsync(() => fetchJournalEntries(), [])
  const [content, setContent] = useState('')
  const [moodEmoji, setMoodEmoji] = useState(null)
  const [expanded, setExpanded] = useState(null)

  async function save() {
    if (!content.trim()) return
    try {
      await createJournalEntry({
        date: todayISO(),
        content: content.trim(),
        mood_emoji: moodEmoji
      })
      toast.success('Entrada guardada ✓')
      setContent('')
      setMoodEmoji(null)
      entriesQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <div className="space-y-4">
      {/* New entry */}
      <Card title="Nueva entrada" emoji="✏️">
        <div className="mb-3">
          <label className="label">¿Cómo fue el día?</label>
          <div className="flex gap-2 mb-3">
            {MOOD_EMOJIS.map((e) => (
              <button
                key={e}
                onClick={() => setMoodEmoji(moodEmoji === e ? null : e)}
                className={`text-2xl transition-all ${moodEmoji === e ? 'scale-125' : 'opacity-40 hover:opacity-80'}`}
              >{e}</button>
            ))}
          </div>
          <textarea
            className="input min-h-[120px] resize-none"
            placeholder="Escribí lo que sea…"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
        </div>
        <Button onClick={save} color="purple" className="w-full">Guardar entrada</Button>
      </Card>

      {/* Entry list */}
      <Card title="Entradas" emoji="📓">
        {!(entriesQ.data || []).length ? (
          <EmptyState icon="📓" title="Sin entradas" description="Empezá a escribir tu diario hoy." />
        ) : (
          <ul className="space-y-2">
            {entriesQ.data.map((entry) => (
              <li key={entry.id}
                className="rounded-[14px] overflow-hidden"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.06)' }}
              >
                <button
                  onClick={() => setExpanded(expanded === entry.id ? null : entry.id)}
                  className="w-full text-left px-4 py-3 group"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      {entry.mood_emoji && <span className="text-lg">{entry.mood_emoji}</span>}
                      <div>
                        <div className="text-sm font-semibold">{fmt(entry.date, "EEEE d 'de' MMM").replace(/^\w/, c => c.toUpperCase())}</div>
                        <div className="text-[11px] text-white/30">{fmt(entry.created_at, 'HH:mm')}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          deleteJournalEntry(entry.id).then(() => { toast.success('Eliminada'); entriesQ.refetch() })
                        }}
                        className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs"
                      >✕</button>
                      <span className="text-white/25 text-xs">{expanded === entry.id ? '▲' : '▼'}</span>
                    </div>
                  </div>
                  {expanded !== entry.id && (
                    <p className="text-xs text-white/40 mt-1 line-clamp-1">{entry.content}</p>
                  )}
                </button>
                {expanded === entry.id && (
                  <div className="px-4 pb-4">
                    <p className="text-sm text-white/80 whitespace-pre-wrap">{entry.content}</p>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  )
}
