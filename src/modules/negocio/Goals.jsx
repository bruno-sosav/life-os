import { useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchGoals, createGoal, updateGoal, deleteGoal } from './queries.js'
import { fmt } from '../../lib/dates.js'
import { toast } from '../../store/toastStore.js'

export default function Goals() {
  const goalsQ = useAsync(() => fetchGoals(new Date()), [])
  const [title, setTitle] = useState('')

  async function add() {
    if (!title.trim()) return
    try {
      await createGoal({ title: title.trim() })
      toast.success('Objetivo agregado ✓')
      setTitle('')
      goalsQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  async function setProgress(id, val) {
    try {
      await updateGoal(id, { progress: val, completed: val >= 100 })
      goalsQ.refetch()
    } catch (e) { toast.error(e.message) }
  }

  return (
    <Card title={`Objetivos · ${fmt(new Date(), "MMMM").replace(/^\w/, c => c.toUpperCase())}`} emoji="🎯">
      <div className="flex gap-2 mb-4">
        <input className="input" placeholder="Nuevo objetivo del mes…" value={title} onChange={(e) => setTitle(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && add()} />
        <Button onClick={add}>+</Button>
      </div>
      {!(goalsQ.data || []).length ? (
        <p className="text-sm text-white/30 text-center py-4">Sin objetivos este mes.</p>
      ) : (
        <ul className="space-y-4">
          {goalsQ.data.map((g) => (
            <li key={g.id} className="group">
              <div className="flex items-center justify-between mb-1.5">
                <span className={`text-sm font-medium ${g.completed ? 'text-[#30D158] line-through opacity-60' : ''}`}>{g.title}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold" style={{ color: g.progress >= 100 ? '#30D158' : 'rgba(255,255,255,0.4)' }}>{g.progress}%</span>
                  <button onClick={() => deleteGoal(g.id).then(() => { toast.success('Eliminado'); goalsQ.refetch() })}
                    className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs">✕</button>
                </div>
              </div>
              <div className="h-1.5 bg-white/[0.07] rounded-full overflow-hidden mb-1.5">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${g.progress}%`, background: g.progress >= 100 ? '#30D158' : '#0A84FF' }}
                />
              </div>
              <input
                type="range" min={0} max={100} step={5}
                value={g.progress}
                onChange={(e) => setProgress(g.id, Number(e.target.value))}
                className="w-full accent-[#0A84FF] opacity-0 group-hover:opacity-100 transition h-1"
              />
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
