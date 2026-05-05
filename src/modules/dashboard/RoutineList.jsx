import { useMemo } from 'react'
import RoutineItem from './RoutineItem.jsx'
import { CATEGORY_COLORS } from '../../lib/constants.js'

const SECTIONS = [
  { label: 'Mañana',   start: 0,  end: 12 * 60 },
  { label: 'Tarde',    start: 12 * 60, end: 20 * 60 },
  { label: 'Noche',    start: 20 * 60, end: 24 * 60 },
  { label: 'Sin hora', start: -1, end: -1 }
]

function toMinutes(item) {
  if (item._type === 'block') return item.hour_start * 60 + (item.hour_min ?? 0)
  if (item.start_time) {
    const [h, m] = item.start_time.split(':').map(Number)
    return h * 60 + (m || 0)
  }
  return null
}

export default function RoutineList({
  blocks, blockCompletions, habits, habitLogs, dateISO,
  onToggleBlock, onToggleHabit, onEditBlock, onEditHabit
}) {
  const completedBlocks = useMemo(
    () => new Set((blockCompletions || []).map((c) => c.block_id)),
    [blockCompletions]
  )
  const completedHabits = useMemo(() => {
    const m = {}
    ;(habitLogs || []).filter((l) => l.date === dateISO && l.completed).forEach((l) => { m[l.habit_id] = true })
    return m
  }, [habitLogs, dateISO])

  const allItems = useMemo(() => {
    const bItems = (blocks || []).map((b) => ({
      ...b,
      _type: 'block',
      color: b.color || CATEGORY_COLORS[b.category] || CATEGORY_COLORS.default,
      _min: b.hour_start * 60 + (b.hour_min ?? 0),
      _done: completedBlocks.has(b.id)
    }))
    const hItems = (habits || []).map((h) => ({
      ...h,
      _type: 'habit',
      color: h.color || '#30D158',
      _min: (() => {
        if (!h.start_time) return null
        const [hh, mm] = h.start_time.split(':').map(Number)
        return hh * 60 + (mm || 0)
      })(),
      _done: !!completedHabits[h.id]
    }))
    return [...bItems, ...hItems].sort((a, b) => {
      if (a._min == null && b._min == null) return 0
      if (a._min == null) return 1
      if (b._min == null) return -1
      return a._min - b._min
    })
  }, [blocks, habits, completedBlocks, completedHabits])

  const withoutTime = allItems.filter((it) => it._min == null)
  const timed = allItems.filter((it) => it._min != null)

  function itemsInSection(start, end) {
    return timed.filter((it) => it._min >= start && it._min < end)
  }

  function renderItem(it) {
    return (
      <RoutineItem
        key={`${it._type}-${it.id}`}
        item={it}
        done={it._done}
        onToggle={() => it._type === 'block' ? onToggleBlock(it) : onToggleHabit(it)}
        onEdit={() => it._type === 'block' ? onEditBlock?.(it) : onEditHabit?.(it)}
      />
    )
  }

  if (allItems.length === 0) {
    return (
      <div className="text-center py-10 text-white/30 text-sm">
        Sin actividades para este día.<br />
        <span className="text-xs">Tocá "Editar rutina" para agregar.</span>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {SECTIONS.slice(0, 3).map((sec) => {
        const items = itemsInSection(sec.start, sec.end)
        if (!items.length) return null
        return (
          <div key={sec.label}>
            <div className="section-header mt-5 first:mt-0">{sec.label}</div>
            {items.map(renderItem)}
          </div>
        )
      })}
      {withoutTime.length > 0 && (
        <div>
          <div className="section-header mt-5">Sin horario</div>
          {withoutTime.map(renderItem)}
        </div>
      )}
    </div>
  )
}
