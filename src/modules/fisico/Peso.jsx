import { useMemo, useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Tabs from '../../components/Tabs.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import {
  fetchWeightLogs,
  upsertWeightLog,
  fetchNutritionLogs,
  upsertNutritionLog
} from './queries.js'
import { todayISO } from '../../lib/dates.js'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine
} from 'recharts'

const RANGES = [
  { value: 30, label: '30d' },
  { value: 90, label: '90d' },
  { value: 180, label: '180d' },
  { value: 365, label: '1a' }
]

export default function Peso() {
  const [range, setRange] = useState(30)
  const [goal, setGoal] = useState(() => Number(localStorage.getItem('lifeos.weight.goal') || 0))
  const weightQ = useAsync(() => fetchWeightLogs(range), [range])
  const nutritionQ = useAsync(() => fetchNutritionLogs(30), [])

  const today = todayISO()
  const todayNut = (nutritionQ.data || []).find((n) => n.date === today)
  const todayWeight = (weightQ.data || []).find((w) => w.date === today)

  const [w, setW] = useState('')
  const [q, setQ] = useState(todayNut?.quality_score || 3)
  const [meals, setMeals] = useState(todayNut?.meals_count || 3)
  const [water, setWater] = useState(todayNut?.water_liters || 2)

  async function saveWeight() {
    if (!w) return
    await upsertWeightLog({ date: today, weight_kg: Number(w), notes: null })
    setW('')
    weightQ.refetch()
  }

  async function saveNutrition() {
    await upsertNutritionLog({
      date: today,
      quality_score: q,
      meals_count: meals,
      water_liters: water,
      notes: null
    })
    nutritionQ.refetch()
  }

  function saveGoal(v) {
    setGoal(v)
    localStorage.setItem('lifeos.weight.goal', String(v))
  }

  const chartData = useMemo(
    () => (weightQ.data || []).map((w) => ({ date: w.date, weight: Number(w.weight_kg) })),
    [weightQ.data]
  )

  const avgQuality = useMemo(() => {
    const last7 = (nutritionQ.data || []).slice(-7)
    if (!last7.length) return 0
    return (last7.reduce((sum, n) => sum + (n.quality_score || 0), 0) / last7.length).toFixed(1)
  }, [nutritionQ.data])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <Card
        title="Peso"
        subtitle={todayWeight ? `Hoy: ${todayWeight.weight_kg} kg` : 'Sin registro hoy'}
        action={
          <Tabs value={range} onChange={setRange} items={RANGES} />
        }
        className="lg:col-span-2"
      >
        <div className="h-56">
          {chartData.length > 1 ? (
            <ResponsiveContainer>
              <LineChart data={chartData}>
                <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
                <XAxis dataKey="date" stroke="#5b5b68" fontSize={10} />
                <YAxis stroke="#5b5b68" fontSize={10} domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip
                  contentStyle={{ background: '#1d1d22', border: '1px solid rgba(255,255,255,0.06)', borderRadius: 8 }}
                />
                {goal > 0 && (
                  <ReferenceLine y={goal} stroke="#1D9E75" strokeDasharray="4 4" label={{ value: `Meta ${goal}kg`, position: 'right', fill: '#1D9E75', fontSize: 10 }} />
                )}
                <Line type="monotone" dataKey="weight" stroke="#7F77DD" strokeWidth={2.5} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full grid place-items-center text-xs text-ink-400">Necesitás al menos 2 registros</div>
          )}
        </div>
        <div className="mt-3 flex items-end gap-2">
          <div className="flex-1">
            <label className="label">Registrar hoy (kg)</label>
            <input type="number" step="0.1" className="input" value={w} onChange={(e) => setW(e.target.value)} placeholder="78.4" />
          </div>
          <Button onClick={saveWeight}>Guardar</Button>
        </div>
        <div className="mt-3 flex items-center gap-2 text-xs text-ink-300">
          <span>Meta:</span>
          <input
            type="number" step="0.1" className="input !py-1 max-w-[100px] text-xs"
            value={goal || ''} onChange={(e) => saveGoal(Number(e.target.value))}
            placeholder="kg"
          />
        </div>
      </Card>

      <Card title="Nutrición de hoy" subtitle={`Promedio 7d: ${avgQuality}/5`}>
        <div className="space-y-3">
          <div>
            <label className="label">Calidad</label>
            <div className="flex gap-1">
              {[1,2,3,4,5].map((n) => (
                <button
                  key={n}
                  onClick={() => setQ(n)}
                  className={`text-2xl transition ${n <= q ? 'opacity-100' : 'opacity-30'}`}
                >★</button>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Comidas</label>
              <input type="number" min={0} max={10} className="input" value={meals} onChange={(e) => setMeals(Number(e.target.value))} />
            </div>
            <div>
              <label className="label">Agua (L)</label>
              <input type="number" min={0} step="0.25" className="input" value={water} onChange={(e) => setWater(Number(e.target.value))} />
            </div>
          </div>
          <Button className="w-full" onClick={saveNutrition}>Guardar nutrición</Button>
        </div>
      </Card>
    </div>
  )
}
