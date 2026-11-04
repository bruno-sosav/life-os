import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function AgendaItem({ item, color, onToggle, onEdit, onDelete }) {
  const done = item.done
  const [localDone, setLocalDone] = useState(done)
  const [busy, setBusy] = useState(false)

  // Sync cuando cambia desde afuera (refetch del padre)
  useEffect(() => { setLocalDone(done) }, [done])

  async function handleToggle() {
    if (busy) return
    const next = !localDone
    setLocalDone(next)      // optimistic: UI responde de inmediato
    setBusy(true)
    try {
      await onToggle()
    } catch {
      setLocalDone(localDone) // revertir si falla
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      className="group flex items-center gap-3 px-3 py-3 rounded-xl active:bg-ink-700 hover:bg-ink-900 transition-colors cursor-pointer select-none"
      onClick={handleToggle}
    >
      {/* Checkbox animado */}
      <motion.div
        className="shrink-0 w-6 h-6 rounded-full border-2 grid place-items-center"
        animate={{
          borderColor: localDone ? color : '#5E6662',
          backgroundColor: localDone ? color : 'rgba(0,0,0,0)',
          scale: busy ? 0.9 : 1,
        }}
        transition={{ type: 'spring', stiffness: 480, damping: 26 }}
      >
        <AnimatePresence initial={false}>
          {localDone && (
            <motion.svg
              key="check"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              transition={{ type: 'spring', stiffness: 600, damping: 22 }}
              width="11" height="11" viewBox="0 0 12 12" fill="none"
            >
              <path d="M2.5 6l2.8 2.8 4.2-4.8" stroke="#07090A" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            </motion.svg>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Hora */}
      {item.time && (
        <span className="font-mono text-xs text-ink-400 w-11 shrink-0">{item.time}</span>
      )}

      {/* Nombre */}
      <span className={`flex-1 text-[15px] font-medium leading-snug transition-colors duration-200 ${localDone ? 'line-through text-ink-400' : 'text-ink-100'}`}>
        {item.title}
      </span>

      {/* Categoría pill */}
      {item.category && (
        <span className="text-[10px] font-bold tracking-wider uppercase shrink-0 hidden sm:inline" style={{ color }}>
          {item.category}
        </span>
      )}

      {/* Acciones */}
      <div className="md:opacity-0 md:group-hover:opacity-100 md:focus-within:opacity-100 flex items-center gap-0.5 transition-opacity shrink-0">
        <button
          onClick={(e) => { e.stopPropagation(); onEdit?.() }}
          className="w-9 h-9 md:w-7 md:h-7 rounded-lg text-ink-400 hover:text-ink-300 hover:bg-ink-700 text-sm grid place-items-center transition"
          title="Editar"
          aria-label={`Editar ${item.title}`}
        >✎</button>
        {onDelete && (
          <button
            onClick={(e) => { e.stopPropagation(); onDelete?.() }}
            className="w-9 h-9 md:w-7 md:h-7 rounded-lg text-ink-400 hover:text-down hover:bg-ink-700 text-sm grid place-items-center transition"
            title="Eliminar"
            aria-label={`Eliminar ${item.title}`}
          >✕</button>
        )}
      </div>
    </div>
  )
}
