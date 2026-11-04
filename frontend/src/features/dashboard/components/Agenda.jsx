import AgendaItem from './AgendaItem.jsx'
import { colorFor } from '../../../shared/lib/constants.js'

// Color de cada ítem: el propio, o el de su categoría (bloques) / verde (hábitos)
function itemColor(item) {
  if (item.color) return item.color
  return item.kind === 'block'
    ? (item.category ? colorFor(item.category) : '#8C948F')
    : '#2EBD85'
}

export default function Agenda({ sections, onToggle, onEditBlock, onEditHabit, onDeleteHabit }) {
  if (sections.length === 0) {
    return (
      <div className="text-center py-10 text-ink-400 text-sm">
        Nada agendado este día.<br />
        <span className="text-xs">Agregá un bloque o un hábito con los botones de arriba.</span>
      </div>
    )
  }

  return (
    <div className="space-y-1">
      {sections.map((section, i) => (
        <div key={section.key}>
          <div className={`section-header ${i === 0 ? '' : 'mt-5'}`}>{section.label}</div>
          {section.items.map((item) => (
            <AgendaItem
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
