import { useState } from 'react'
import { addMonths, startOfMonth } from 'date-fns'
import { AnimatePresence, motion } from 'framer-motion'
import Card from '../../../shared/components/ui/Card.jsx'
import MonthGrid from '../../../shared/components/calendar/MonthGrid.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fmt, todayISO } from '../../../shared/lib/dates.js'
import { swap } from '../../../shared/lib/motion.js'
import { fetchCalendar, fetchDay } from '../api/calendario.api.js'

// Cada estado con su color y su texto: el color nunca va solo
const DAY_STATUS = {
  cumplido: { color: '#2EBD85', label: 'Cumplido', text: 'text-up' },
  parcial: { color: '#E0B84A', label: 'Parcial', text: 'text-warn' },
  sin_cumplir: { color: '#F6465D', label: 'Sin cumplir', text: 'text-down' },
  libre: { color: null, label: 'Libre', text: 'text-ink-400' },
  pendiente: { color: null, label: 'Pendiente', text: 'text-ink-400' }
}

const weekColor = (pct) => (pct == null ? 'text-ink-400' : pct >= 70 ? 'text-up' : pct > 0 ? 'text-warn' : 'text-down')
const capitalize = (s) => s.replace(/^\w/, (c) => c.toUpperCase())

// El mes en casillas con el % de cada día y de cada semana; tocar un día muestra qué hiciste
export default function ComplianceCalendar() {
  const [month, setMonth] = useState(() => startOfMonth(new Date()))
  const [selected, setSelected] = useState(todayISO())
  const calendarQ = useAsync(() => fetchCalendar(month), [month])
  const dayQ = useAsync(() => (selected ? fetchDay(selected) : Promise.resolve(null)), [selected])
  const cal = calendarQ.data
  const today = todayISO()
  const selectedDay = cal?.days.find((d) => d.date === selected)

  function move(delta) {
    setMonth(addMonths(month, delta))
    setSelected(null)
  }

  return (
    <Card
      title={capitalize(fmt(month, 'MMMM yyyy'))}
      subtitle={cal && (
        <span className="font-mono">
          <span className="text-up">{cal.cumplido}</span> cumplidos · <span className="text-warn">{cal.parcial}</span> parciales · <span className="text-down">{cal.sin_cumplir}</span> sin cumplir
        </span>
      )}
      action={
        <div className="flex gap-1">
          <button onClick={() => move(-1)} aria-label="Mes anterior" className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">‹</button>
          <button onClick={() => move(1)} aria-label="Mes siguiente" className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">›</button>
        </div>
      }
    >
      <MonthGrid
        days={cal?.days || []}
        renderWeek={(i) => {
          const week = cal?.weeks[i]
          return (
            <div className="h-12 flex flex-col items-center justify-center">
              <span className={`font-mono text-xs font-bold ${weekColor(week?.pct)}`}>{week?.pct != null ? `${week.pct}%` : '—'}</span>
            </div>
          )
        }}
        renderDay={(day) => {
          const status = DAY_STATUS[day.status]
          const isSelected = day.date === selected
          const isToday = day.date === today
          return (
            <button
              onClick={() => setSelected(isSelected ? null : day.date)}
              aria-pressed={isSelected}
              aria-label={`${fmt(day.date, "d 'de' MMMM")}: ${status.label}${day.pct != null ? `, ${day.pct} por ciento` : ''}`}
              className="w-full h-12 rounded-lg border px-1.5 py-1 flex flex-col justify-between text-left transition-transform hover:scale-105"
              style={{
                background: status.color ? `${status.color}1F` : 'transparent',
                borderColor: isSelected ? '#7C5CFF' : status.color ? `${status.color}4D` : isToday ? '#7C5CFF80' : '#1A201E'
              }}
            >
              <span className={`text-[10px] font-semibold font-mono ${status.color ? 'text-ink-100' : 'text-ink-400'}`}>{fmt(day.date, 'd')}</span>
              {day.pct != null && day.status !== 'pendiente' && (
                <span className={`self-end font-mono text-[11px] font-bold ${status.text}`}>{day.pct}%</span>
              )}
            </button>
          )
        }}
      />

      <div className="flex flex-wrap gap-x-4 gap-y-1 mt-3 text-[11px] text-ink-400">
        {['cumplido', 'parcial', 'sin_cumplir'].map((key) => (
          <span key={key} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm" style={{ background: DAY_STATUS[key].color }} />
            {DAY_STATUS[key].label}
          </span>
        ))}
        <span>· 70 % o más de lo agendado es cumplido</span>
      </div>

      <AnimatePresence mode="wait">
        {selectedDay && dayQ.data && (
          <motion.div key={selected} {...swap} className="mt-4 pt-4 border-t border-ink-700">
            <div className="flex items-baseline justify-between mb-2">
              <span className="text-sm font-semibold">{capitalize(fmt(selected, "EEEE d 'de' MMMM"))}</span>
              <span className={`text-[10px] font-bold tracking-wider uppercase ${DAY_STATUS[selectedDay.status].text}`}>
                {DAY_STATUS[selectedDay.status].label}
              </span>
            </div>
            {selectedDay.expected ? (
              <>
                <div className="font-mono text-lg font-bold mb-2">
                  {selectedDay.done} <span className="text-ink-400 text-sm">/ {selectedDay.expected}</span>
                </div>
                <ul className="space-y-1.5">
                  {dayQ.data.sections.flatMap((s) => s.items).map((it) => (
                    <li key={`${it.kind}-${it.id}`} className="flex justify-between text-sm">
                      <span className={it.done ? '' : 'text-ink-400'}>{it.title}</span>
                      <span className={`text-[10px] font-bold tracking-wider ${it.done ? 'text-up' : selected < today ? 'text-down' : 'text-ink-400'}`}>
                        {it.done ? 'HECHO' : selected < today ? 'FALTÓ' : 'PENDIENTE'}
                      </span>
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <p className="text-sm text-ink-400">No había nada agendado.</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  )
}
