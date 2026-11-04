import { parseISO } from 'date-fns'

const HEADS = ['L', 'M', 'X', 'J', 'V', 'S', 'D']

// Calendario del mes con casillas, lunes primero. Cada pantalla decide qué va en cada día.
// `days`: [{ date: 'yyyy-MM-dd', ... }] del mes en orden; `renderDay(day)` dibuja la casilla.
export default function MonthGrid({ days, renderDay }) {
  const offset = days.length ? (parseISO(days[0].date).getDay() + 6) % 7 : 0
  return (
    <div className="grid grid-cols-7 gap-1">
      {HEADS.map((h) => (
        <span key={h} className="text-[10px] text-center text-ink-400 font-semibold tracking-wider py-1">{h}</span>
      ))}
      {Array.from({ length: offset }, (_, i) => <span key={`blank-${i}`} />)}
      {days.map((day) => <div key={day.date}>{renderDay(day)}</div>)}
    </div>
  )
}
