import { parseISO } from 'date-fns'

const HEADS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

// Calendario del mes con casillas, lunes primero. Cada pantalla decide qué va en cada día.
// `days`: [{ date: 'yyyy-MM-dd', ... }] del mes en orden; `renderDay(day)` dibuja la casilla.
// `renderWeek(i)`, opcional, agrega al final de cada fila una columna con el total de la semana i.
export default function MonthGrid({ days, renderDay, renderWeek, weekLabel = 'SEM' }) {
  const offset = days.length ? (parseISO(days[0].date).getDay() + 6) % 7 : 0
  const cells = [...Array(offset).fill(null), ...days]
  while (cells.length % 7) cells.push(null)
  const weeks = Array.from({ length: cells.length / 7 }, (_, i) => cells.slice(i * 7, i * 7 + 7))
  const columns = renderWeek ? 'grid-cols-[repeat(7,minmax(0,1fr))_44px]' : 'grid-cols-7'

  return (
    <div className={`grid ${columns} gap-1`}>
      {HEADS.map((h) => (
        <span key={h} className="text-[10px] text-center text-ink-400 font-semibold tracking-wider py-1">{h}</span>
      ))}
      {renderWeek && <span className="text-[10px] text-center text-ink-400 font-semibold tracking-wider py-1">{weekLabel}</span>}
      {weeks.map((week, i) => [
        ...week.map((day, j) => <div key={day?.date ?? `blank-${i}-${j}`}>{day && renderDay(day)}</div>),
        renderWeek && <div key={`week-${i}`}>{renderWeek(i)}</div>
      ])}
    </div>
  )
}
