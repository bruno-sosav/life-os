import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PageHeader from '../../../components/PageHeader.jsx'
import EmptyState from '../../../components/EmptyState.jsx'
import Button from '../../../components/Button.jsx'
import { useAsync } from '../../../hooks/useAsync.js'
import { swap } from '../../../lib/motion.js'
import { fetchProjects } from '../api/proyectos.api.js'
import { fetchBoard } from '../api/tareas.api.js'
import ProjectTabs from '../components/ProjectTabs.jsx'
import Board from '../components/Board.jsx'
import Ideas from '../components/Ideas.jsx'
import Goals from '../components/Goals.jsx'

export default function NegocioPage() {
  const projectsQ = useAsync(() => fetchProjects(), [])
  const projects = projectsQ.data || []
  const [selected, setSelected] = useState(null)
  // Cada tablero recuerda de qué proyecto es: al cambiar, no se ve un instante el anterior
  const boardQ = useAsync(
    () => (selected ? fetchBoard(selected).then((columns) => ({ projectId: selected, columns })) : Promise.resolve(null)),
    [selected]
  )
  const board = boardQ.data?.projectId === selected ? boardQ.data : null

  // Arranca en el primer proyecto (o en el que se acaba de crear)
  useEffect(() => {
    if (!selected && projects.length) setSelected(projects[0].id)
  }, [projects, selected])

  async function onCreated(project) {
    await projectsQ.refetch()
    setSelected(project.id)
  }

  // Al borrar el proyecto que estabas viendo, el tablero pasa al primero que quede
  async function onDeleted() {
    setSelected(null)
    await projectsQ.refetch()
  }

  return (
    <div>
      <PageHeader title="Negocio" subtitle="Un tablero por proyecto, ideas y objetivos del mes" />

      {projectsQ.data && !projects.length ? (
        <div className="card-pad mb-4">
          <EmptyState icon="▦" title="Sin proyectos" description="Cada proyecto tiene su tablero: pendiente, en proceso y finalizado." />
          <ProjectTabs projects={[]} selected={null} onSelect={setSelected} onCreated={onCreated} onChanged={projectsQ.refetch} onDeleted={onDeleted} />
        </div>
      ) : (
        <ProjectTabs projects={projects} selected={selected} onSelect={setSelected} onCreated={onCreated} onChanged={projectsQ.refetch} onDeleted={onDeleted} />
      )}

      <AnimatePresence mode="wait">
        {board && (
          <motion.div key={board.projectId} {...swap}>
            <Board
              board={board.columns}
              setBoard={(columns) => boardQ.setData({ ...board, columns })}
              projects={projects}
              projectId={selected}
              onChanged={boardQ.refetch}
            />
          </motion.div>
        )}
      </AnimatePresence>
      {boardQ.error && (
        <div className="card-pad text-sm text-ink-400 flex items-center justify-between">
          No se pudo cargar el tablero. <Button size="sm" variant="secondary" onClick={boardQ.refetch}>Reintentar</Button>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <Ideas />
        <Goals />
      </div>
    </div>
  )
}
