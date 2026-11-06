import { fmt, todayISO } from '../../../shared/lib/dates.js'

const DOW = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']

// Lunes a domingo: cada día muestra un punto por cada tipo que entrenaste
export default function WeekStrip({ data, colorOf }) {
  const today = todayISO()
  return (
    <div className="card-pad">
      <div className="flex items-baseline justify-between mb-3">
        <h3 className="font-semibold text-base">Esta semana</h3>
        <span className="text-xs text-ink-400">
          <span className="font-mono text-lg font-bold text-up mr-1">{data?.count ?? 0}</span>{data?.count === 1 ? 'entreno' : 'entrenos'}
        </span>
      </div>
      <div className="grid grid-cols-7 gap-1.5">
        {(data?.days || []).map((day, i) => {
          const trained = day.activity_ids.length > 0
          const isToday = day.date === today
          return (
            <div key={day.date}
              className={`flex flex-col items-center gap-1.5 py-2.5 rounded-xl border ${
                isToday ? 'border-accent' : trained ? 'border-ink-600 bg-ink-700' : 'border-ink-700'
              }`}>
              <span className={`text-[10px] font-semibold ${isToday ? 'text-accent' : 'text-ink-400'}`}>{DOW[i]}</span>
              <span className={`font-mono text-sm font-semibold ${trained ? 'text-ink-100' : 'text-ink-400'}`}>{fmt(day.date, 'd')}</span>
              <span className="flex gap-0.5 h-1.5">
                {day.activity_ids.map((id) => <span key={id} className="w-1.5 h-1.5 rounded-full" style={{ background: colorOf(id) }} />)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
