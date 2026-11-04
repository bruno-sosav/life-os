import { Draggable } from '@hello-pangea/dnd'
import { PRIORITY_COLORS } from '../../../lib/constants.js'
import { fmt } from '../../../lib/dates.js'

// Al levantarla se agranda, se inclina y proyecta sombra; al soltarla se acomoda sin inclinación
function cardStyle(style, snapshot) {
  if (snapshot.isDropAnimating) {
    return { ...style, transition: 'all 0.28s cubic-bezier(0.2, 1, 0.3, 1)' }
  }
  if (!snapshot.isDragging) return style
  return {
    ...style,
    transform: `${style.transform ?? ''} rotate(2deg) scale(1.03)`,
    boxShadow: '0 16px 32px rgba(0, 0, 0, 0.55)'
  }
}

export default function TaskCard({ task, index, onOpen, onToggleDone }) {
  const done = task.status === 'hecho'
  return (
    // La tarjeta es casi toda botones: sin esto la librería no deja empezar a arrastrar desde ellos
    <Draggable draggableId={task.id} index={index} disableInteractiveElementBlocking>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={cardStyle(provided.draggableProps.style, snapshot)}
          className={`rounded-xl p-3 border bg-ink-900 transition-colors ${
            snapshot.isDragging ? 'border-accent' : 'border-ink-700 hover:border-ink-600'
          }`}
        >
          <div className="flex items-start gap-2.5">
            <button
              onClick={() => onToggleDone(task)}
              aria-label={done ? `Volver a pendiente: ${task.title}` : `Finalizar: ${task.title}`}
              className={`ios-checkbox mt-0.5 w-5 h-5 rounded-full border-2 grid place-items-center shrink-0 ${
                done ? 'bg-up border-up' : 'border-ink-500 hover:border-up'
              }`}
            >
              {done && <span className="text-ink-950 text-[9px] font-bold">✓</span>}
            </button>
            <button onClick={() => onOpen(task)} className="flex-1 min-w-0 text-left">
              <div className={`text-sm font-medium leading-snug ${done ? 'line-through text-ink-400' : ''}`}>
                {task.title}
              </div>
              <div className="flex items-center gap-3 mt-1.5">
                <span className="text-[10px] font-bold tracking-wider uppercase" style={{ color: PRIORITY_COLORS[task.priority] }}>
                  {task.priority}
                </span>
                {task.due_date && (
                  <span className="font-mono text-[11px] text-ink-400">{fmt(task.due_date, 'd MMM')}</span>
                )}
              </div>
            </button>
          </div>
        </div>
      )}
    </Draggable>
  )
}
