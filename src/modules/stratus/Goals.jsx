import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchGoals, createGoal, updateGoal, deleteGoal } from './queries.js'
import { fmt } from '../../lib/dates.js'

export default function Goals() {
  const goalsQ = useAsync(() => fetchGoals(new Date()), [])
  const [title, setTitle] = useState('')

  async function add() {
    if (!title.trim()) return
    await createGoal({ title: title.trim() })
    setTitle('')
    goalsQ.refetch()
  }

  async function setProgress(id, val) {
    await updateGoal(id, { progress: val, completed: val >= 100 })
    goalsQ.refetch()
  }

  return (
    <Card title={`Objetivos · ${fmt(new Date(), 'MMMM').replace(/^./, c => c.toUpperCase())}`}>
      <div className="flex gap-2 mb-3">
        <input
          className="input"
          placeholder="Nuevo objetivo del mes…"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && add()}
        />
        <Button onClick={add}>+</Button>
      </div>
      {(goalsQ.data || []).length === 0 ? (
        <p className="text-sm text-ink-400 text-center py-4">Sin objetivos este mes.</p>
      ) : (
        <ul className="space-y-3">
          {goalsQ.data.map((g) => (
            <li key={g.id} className="group">
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-sm ${g.completed ? 'text-teal-brand line-through' : ''}`}>{g.title}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-ink-400">{g.progress}%</span>
                  <button
                    onClick={() => deleteGoal(g.id).then(goalsQ.refetch)}
                    className="opacity-0 group-hover:opacity-100 text-ink-400 hover:text-coral-brand text-xs"
                  >✕</button>
                </div>
              </div>
              <input
                type="range" min={0} max={100} step={5}
                value={g.progress}
                onChange={(e) => setProgress(g.id, Number(e.target.value))}
                className="w-full accent-purple-brand"
              />
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
