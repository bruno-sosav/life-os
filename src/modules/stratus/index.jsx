import { useMemo, useState } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Kanban from './Kanban.jsx'
import Ideas from './Ideas.jsx'
import Goals from './Goals.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchTasks } from './queries.js'

export default function Stratus() {
  const tasksQ = useAsync(() => fetchTasks(), [])
  const [project, setProject] = useState('all')

  const projects = useMemo(() => {
    const s = new Set()
    ;(tasksQ.data || []).forEach((t) => t.project && s.add(t.project))
    return Array.from(s).sort()
  }, [tasksQ.data])

  return (
    <div>
      <PageHeader
        title="Stratus"
        subtitle="Negocio, tareas, ideas y objetivos"
        actions={
          <select
            className="input !py-1.5 max-w-[200px] text-sm"
            value={project}
            onChange={(e) => setProject(e.target.value)}
          >
            <option value="all">Todos los proyectos</option>
            {projects.map((p) => <option key={p} value={p}>{p}</option>)}
          </select>
        }
      />

      <Kanban
        tasks={tasksQ.data || []}
        projectFilter={project}
        onChange={tasksQ.refetch}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        <Ideas />
        <Goals />
      </div>
    </div>
  )
}
