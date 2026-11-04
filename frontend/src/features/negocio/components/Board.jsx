import { useState } from 'react'
import { DragDropContext, Droppable } from '@hello-pangea/dnd'
import { STATUS_LABELS } from '../../../shared/lib/constants.js'
import { toast } from '../../../shared/store/toastStore.js'
import { moveTask, updateTask } from '../api/tareas.api.js'
import TaskCard from './TaskCard.jsx'
import TaskModal from './TaskModal.jsx'

const COLUMNS = Object.keys(STATUS_LABELS)
const DOT = { pendiente: 'bg-ink-400', en_progreso: 'bg-warn', hecho: 'bg-up' }

// La tarea pasa de una columna (o lugar) a otra en la copia local del tablero
function moved(board, { source, destination }) {
  const from = source.droppableId
  const to = destination.droppableId
  const next = { ...board, [from]: [...board[from]] }
  const [task] = next[from].splice(source.index, 1)
  if (to !== from) next[to] = [...board[to]]
  next[to].splice(destination.index, 0, { ...task, status: to })
  return next
}

export default function Board({ board, setBoard, projects, projectId, onChanged }) {
  const [modal, setModal] = useState(null) // null = cerrado; { task } o { status } para una nueva

  // La pantalla se actualiza al instante y se guarda atrás; si falla, vuelve a lo del backend
  async function onDragEnd(result) {
    const { destination, source, draggableId } = result
    if (!destination) return
    if (destination.droppableId === source.droppableId && destination.index === source.index) return
    setBoard(moved(board, result))
    try {
      await moveTask(draggableId, destination.droppableId, destination.index)
    } catch (e) {
      toast.error('No se pudo mover: ' + e.message)
      onChanged()
    }
  }

  async function toggleDone(task) {
    try {
      await updateTask(task.id, { status: task.status === 'hecho' ? 'pendiente' : 'hecho' })
      onChanged()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <DragDropContext onDragEnd={onDragEnd}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {COLUMNS.map((col) => (
          <Droppable droppableId={col} key={col}>
            {(provided, snapshot) => (
              <section
                ref={provided.innerRef}
                {...provided.droppableProps}
                aria-label={STATUS_LABELS[col]}
                className={`rounded-2xl border p-3 min-h-[180px] transition-colors duration-200 ${
                  snapshot.isDraggingOver ? 'bg-up/5 border-up/30' : 'bg-ink-800 border-ink-700'
                }`}
              >
                <header className="flex items-center justify-between mb-3 px-1">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${DOT[col]}`} />
                    <h3 className="font-semibold text-sm">{STATUS_LABELS[col]}</h3>
                    <span className="font-mono text-[11px] text-ink-400">{board[col].length}</span>
                  </div>
                  <button
                    onClick={() => setModal({ status: col })}
                    aria-label={`Nueva tarea en ${STATUS_LABELS[col]}`}
                    className="w-8 h-8 rounded-lg hover:bg-ink-700 grid place-items-center text-ink-400 hover:text-ink-100 transition"
                  >+</button>
                </header>
                <div className="space-y-2">
                  {board[col].map((task, i) => (
                    <TaskCard key={task.id} task={task} index={i} onOpen={(t) => setModal({ task: t })} onToggleDone={toggleDone} />
                  ))}
                  {provided.placeholder}
                </div>
              </section>
            )}
          </Droppable>
        ))}
      </div>

      <TaskModal
        open={modal !== null}
        task={modal?.task}
        status={modal?.status}
        projectId={projectId}
        projects={projects}
        onClose={() => setModal(null)}
        onSaved={() => { setModal(null); onChanged() }}
      />
    </DragDropContext>
  )
}
