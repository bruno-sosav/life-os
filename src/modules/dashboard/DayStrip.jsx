import { useEffect, useRef } from 'react'
import { format, startOfWeek, addDays } from 'date-fns'
import { es } from 'date-fns/locale'

const DAYS_SHORT = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

export default function DayStrip({ selected, onChange }) {
  const todayDow = (new Date().getDay() + 6) % 7 // 0=lunes
  const weekStart = startOfWeek(new Date(), { weekStartsOn: 1 })
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i))
  const stripRef = useRef(null)

  useEffect(() => {
    if (!stripRef.current) return
    const btn = stripRef.current.children[selected]
    btn?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }, [selected])

  return (
    <div
      ref={stripRef}
      className="flex gap-2 overflow-x-auto pb-1 no-scrollbar"
      style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
    >
      {days.map((day, i) => {
        const isToday = i === todayDow
        const isSelected = i === selected
        const dateNum = format(day, 'd')
        return (
          <button
            key={i}
            onClick={() => onChange(i)}
            className="flex flex-col items-center gap-1 shrink-0 transition-all duration-200 active:scale-95"
          >
            <span className="text-[11px] font-semibold text-white/40 uppercase tracking-wide">
              {DAYS_SHORT[i]}
            </span>
            <span
              className={`w-9 h-9 rounded-full grid place-items-center text-sm font-bold transition-all duration-200 ${
                isSelected
                  ? 'text-white shadow-lg'
                  : isToday
                  ? 'text-[#0A84FF]'
                  : 'text-white/60 hover:text-white'
              }`}
              style={isSelected ? { background: '#0A84FF' } : {}}
            >
              {dateNum}
            </span>
          </button>
        )
      })}
    </div>
  )
}
