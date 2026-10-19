import RoutineItem from './RoutineItem.jsx'
import { CATEGORY_COLORS } from '../../lib/constants.js'

// Color de cada ítem: el propio, o el de su categoría (bloques) / verde (hábitos)
function itemColor(item) {
  if (item.color) return item.color
  return item.kind === 'block'
    ? CATEGORY_COLORS[item.category] || CATEGORY_COLORS.default
    : '#30D158'
}

export default function RoutineList({ sections, onToggle, onEditBlock, onEditHabit, onDeleteHabit }) {
  if (sections.length === 0) {
    return (
      <div className="text-center py-10 text-white/30 text-sm">
        Sin actividades para este día.<br />
        <span className="text-xs">Tocá "Editar rutina" para agregar.</span>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {sections.map((section, i) => (
        <div key={section.key}>
          <div className={`section-header ${i === 0 ? '' : 'mt-5'}`}>{section.label}</div>
          {section.items.map((item) => (
            <RoutineItem
              key={`${item.kind}-${item.id}`}
              item={item}
              color={itemColor(item)}
              onToggle={() => onToggle(item)}
              onEdit={() => item.kind === 'block' ? onEditBlock?.(item.block) : onEditHabit?.(item.habit)}
              onDelete={item.kind === 'habit' ? () => onDeleteHabit?.(item.habit) : undefined}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
