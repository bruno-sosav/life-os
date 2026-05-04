import { useState } from 'react'
import { motion } from 'framer-motion'

export default function RoutineItem({ item, done, onToggle, onEdit }) {
  const [tapping, setTapping] = useState(false)

  async function handleToggle() {
    setTapping(true)
    await onToggle()
    setTimeout(() => setTapping(false), 300)
  }

  const timeLabel = item.hour_start != null
    ? `${String(item.hour_start).padStart(2, '0')}:${String(item.hour_min ?? 0).padStart(2, '0')}`
    : item.start_time?.slice(0, 5) ?? ''

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: done ? 0.5 : 1, y: 0 }}
      className="group flex items-center gap-3 px-3 py-3 rounded-[14px] hover:bg-white/[0.04] transition-colors cursor-pointer"
      onClick={handleToggle}
    >
      {/* Checkbox */}
      <div className="shrink-0">
        <motion.div
          animate={{
            scale: tapping ? [1, 1.25, 1] : 1,
            backgroundColor: done ? item.color : 'transparent'
          }}
          transition={{ type: 'spring', stiffness: 500, damping: 25 }}
          className="w-6 h-6 rounded-full border-2 grid place-items-center ios-checkbox"
          style={{ borderColor: done ? item.color : 'rgba(255,255,255,0.2)' }}
        >
          {done && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 600, damping: 20 }}
              className="text-white text-[11px] font-bold"
            >
              ✓
            </motion.span>
          )}
        </motion.div>
      </div>

      {/* Hora */}
      {timeLabel && (
        <span className="text-xs font-semibold text-white/30 w-10 shrink-0 tabular-nums">{timeLabel}</span>
      )}

      {/* Emoji */}
      {item.emoji && <span className="text-base leading-none shrink-0">{item.emoji}</span>}

      {/* Nombre */}
      <span className={`flex-1 text-sm font-medium ${done ? 'line-through text-white/30' : 'text-white/90'}`}>
        {item.activity ?? item.name}
      </span>

      {/* Categoría / color pill */}
      {item.category && (
        <span
          className="text-[10px] font-semibold px-2 py-0.5 rounded-full shrink-0"
          style={{ background: `${item.color}22`, color: item.color }}
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
    </motion.div>
  )
}
