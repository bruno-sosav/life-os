import { useState } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Kanban from './Kanban.jsx'
import Ideas from './Ideas.jsx'
import Goals from './Goals.jsx'
import ProjectsBar from './ProjectsBar.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchTasks, fetchProjects } from './queries.js'

export default function Negocio() {
  const projectsQ = useAsync(() => fetchProjects(), [])
  const [selectedProject, setSelectedProject] = useState(null)
  const tasksQ = useAsync(() => fetchTasks(selectedProject), [selectedProject])

  return (
    <div>
      <PageHeader title="Negocio" emoji="🏢" subtitle="Tareas, proyectos, ideas y objetivos" />

      <ProjectsBar
        projects={projectsQ.data || []}
        selected={selectedProject}
        onSelect={(id) => setSelectedProject(id)}
        onRefetch={projectsQ.refetch}
      />

      <Kanban
        tasks={tasksQ.data || []}
        projects={projectsQ.data || []}
        projectFilter={selectedProject}
        onChange={tasksQ.refetch}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <Ideas />
        <Goals />
      </div>
    </div>
  )
}
