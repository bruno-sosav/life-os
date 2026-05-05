import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function RoutineItem({ item, done, onToggle, onEdit }) {
  const [localDone, setLocalDone] = useState(done)
  const [busy, setBusy] = useState(false)
  const color = item.color || '#30D158'

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

  const timeLabel = item.hour_start != null
    ? `${String(item.hour_start).padStart(2, '0')}:${String(item.hour_min ?? 0).padStart(2, '0')}`
    : item.start_time?.slice(0, 5) ?? ''

  return (
    <div
      className="group flex items-center gap-3 px-3 py-3.5 rounded-[14px] active:bg-white/[0.06] hover:bg-white/[0.04] transition-colors cursor-pointer select-none"
      onClick={handleToggle}
    >
      {/* Checkbox animado */}
      <motion.div
        className="shrink-0 w-6 h-6 rounded-full border-2 grid place-items-center"
        animate={{
          borderColor: localDone ? color : 'rgba(255,255,255,0.2)',
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
              <path d="M2.5 6l2.8 2.8 4.2-4.8" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            </motion.svg>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Hora */}
      {timeLabel && (
        <span className="text-[11px] font-semibold text-white/35 w-10 shrink-0 tabular-nums">{timeLabel}</span>
      )}

      {/* Emoji */}
      {item.emoji && <span className="text-lg leading-none shrink-0">{item.emoji}</span>}

      {/* Nombre */}
      <span className={`flex-1 text-[15px] font-medium leading-snug transition-colors duration-200 ${localDone ? 'line-through text-white/25' : 'text-white/90'}`}>
        {item.activity ?? item.name}
      </span>

      {/* Categoría pill */}
      {item.category && (
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0 hidden sm:inline"
          style={{ background: `${color}22`, color }}
        >
          {item.category}
        </span>
      )}

      {/* Editar */}
      <button
        onClick={(e) => { e.stopPropagation(); onEdit?.() }}
        className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-white/60 text-xs transition-opacity"
        title="Editar"
      >
        ✎
      </button>
    </div>
  )
}
