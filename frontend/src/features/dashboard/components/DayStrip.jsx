import { useEffect, useRef } from 'react'

const DAYS_SHORT = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

// `week` viene del backend: [{ date: 'yyyy-MM-dd', weekday: 0..6, is_today }]
export default function DayStrip({ week, selected, onChange }) {
  const stripRef = useRef(null)
  const selectedIndex = week.findIndex((d) => d.date === selected)

  useEffect(() => {
    const btn = stripRef.current?.children[selectedIndex]
    btn?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }, [selectedIndex])

  return (
    <div
      ref={stripRef}
      className="flex gap-2 overflow-x-auto pb-1 no-scrollbar"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      {week.map((day) => {
        const isSelected = day.date === selected
        return (
          <button
            key={day.date}
            onClick={() => onChange(day.date)}
            aria-pressed={isSelected}
            className="flex flex-col items-center gap-1 shrink-0 transition-all duration-200 active:scale-95"
          >
            <span className="text-[11px] font-semibold text-ink-400 uppercase tracking-wide">
              {DAYS_SHORT[day.weekday]}
            </span>
            <span
              className={`w-10 h-10 rounded-xl grid place-items-center font-mono text-sm font-semibold border transition-all duration-200 ${
                isSelected
                  ? 'bg-accent border-accent text-ink-100'
                  : day.is_today
                  ? 'border-accent/60 text-accent'
                  : 'border-ink-700 text-ink-300 hover:text-ink-100 hover:border-ink-600'
              }`}
            >
              {Number(day.date.slice(8))}
            </span>
          </button>
        )
      })}
    </div>
  )
}
