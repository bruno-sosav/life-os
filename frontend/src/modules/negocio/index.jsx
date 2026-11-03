import { useState } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Kanban from './Kanban.jsx'
import Ideas from './Ideas.jsx'
import Goals from './Goals.jsx'
import ProjectsBar from './ProjectsBar.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchBoard, fetchProjects } from './queries.js'

export default function Negocio() {
  const projectsQ = useAsync(() => fetchProjects(), [])
  const [selectedProject, setSelectedProject] = useState(null)
  const boardQ = useAsync(() => fetchBoard(selectedProject), [selectedProject])

  return (
    <div>
      <PageHeader title="Negocio" subtitle="Tareas, proyectos, ideas y objetivos" />

      <ProjectsBar
        projects={projectsQ.data || []}
        selected={selectedProject}
        onSelect={(id) => setSelectedProject(id)}
        onRefetch={projectsQ.refetch}
      />

      <Kanban
        board={boardQ.data}
        projects={projectsQ.data || []}
        onChange={boardQ.refetch}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <Ideas />
        <Goals />
      </div>
    </div>
  )
}
