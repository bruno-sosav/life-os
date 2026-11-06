import { addMonths } from 'date-fns'
import Card from '../../../shared/components/ui/Card.jsx'
import MonthGrid from '../../../shared/components/calendar/MonthGrid.jsx'
import { fmt, todayISO } from '../../../shared/lib/dates.js'

const capitalize = (s) => s.replace(/^\w/, (c) => c.toUpperCase())

// El mes en casillas: cada día entrenado se tiñe con el color de lo que hiciste.
// Tocar un día lo selecciona (el historial muestra ese día); tocarlo de nuevo lo suelta.
export default function TrainingCalendar({ month, onMonthChange, data, colorOf, selected, onSelect }) {
  const today = todayISO()
  return (
    <Card
      title={capitalize(fmt(month, 'MMMM yyyy'))}
      subtitle={<><span className="font-mono text-ink-100">{data?.count ?? 0}</span> {data?.count === 1 ? 'día entrenado' : 'días entrenados'}</>}
      action={
        <div className="flex gap-1">
          <button onClick={() => onMonthChange(addMonths(month, -1))} aria-label="Mes anterior"
            className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">‹</button>
          <button onClick={() => onMonthChange(addMonths(month, 1))} aria-label="Mes siguiente"
            className="w-8 h-8 rounded-lg grid place-items-center text-ink-400 hover:text-ink-100 hover:bg-ink-700">›</button>
        </div>
      }
    >
      <MonthGrid
        days={data?.days || []}
        renderDay={(day) => {
          const trained = day.activity_ids.length > 0
          const color = trained ? colorOf(day.activity_ids[0]) : null
          const isSelected = day.date === selected
          return (
            <button
              onClick={() => onSelect(isSelected ? null : day.date)}
              aria-pressed={isSelected}
              aria-label={`${fmt(day.date, "d 'de' MMMM")}${trained ? ', entrenaste' : ''}`}
              className="w-full h-11 rounded-lg border p-1 flex flex-col justify-between transition-transform hover:scale-105"
              style={{
                background: trained ? `${color}26` : 'transparent',
                borderColor: isSelected ? '#7C5CFF' : trained ? `${color}59` : day.date === today ? '#7C5CFF80' : '#1A201E'
              }}
            >
              <span className={`text-[10px] font-semibold font-mono ${trained ? 'text-ink-100' : 'text-ink-400'}`}>{fmt(day.date, 'd')}</span>
              <span className="flex gap-0.5 justify-end">
                {day.activity_ids.map((id) => <span key={id} className="w-1.5 h-1.5 rounded-full" style={{ background: colorOf(id) }} />)}
              </span>
            </button>
          )
        }}
      />
    </Card>
  )
}
