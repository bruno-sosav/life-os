import { useEffect, useMemo, useState } from 'react'
import Card from '../../../shared/components/ui/Card.jsx'
import Button from '../../../shared/components/ui/Button.jsx'
import Tabs from '../../../shared/components/ui/Tabs.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fetchWeightGoal, fetchWeightLogs, saveWeightGoal, upsertWeightLog } from '../api/peso.api.js'
import { fetchNutritionAverage, fetchNutritionLogs, upsertNutritionLog } from '../api/nutricion.api.js'
import { todayISO } from '../../../shared/lib/dates.js'
import { toast } from '../../../shared/store/toastStore.js'
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

export default function PesoNutricion() {
  const [range, setRange] = useState(30)
  const goalQ = useAsync(() => fetchWeightGoal(), [])
  const goal = goalQ.data?.weight_kg ?? null
  const [goalInput, setGoalInput] = useState('')
  const weightQ = useAsync(() => fetchWeightLogs(range), [range])
  const nutritionQ = useAsync(() => fetchNutritionLogs(30), [])
  const nutritionAvgQ = useAsync(() => fetchNutritionAverage(), [])

  const today = todayISO()
  const todayNut = (nutritionQ.data || []).find((n) => n.date === today)
  const todayWeight = (weightQ.data || []).find((w) => w.date === today)

  const [w, setW] = useState('')
  const [q, setQ] = useState(3)
  const [meals, setMeals] = useState(3)
  const [water, setWater] = useState(2)

  // Lo de hoy llega después del primer render: sin esto, guardar pisaba lo cargado con los valores por defecto
  useEffect(() => {
    if (!todayNut) return
    setQ(todayNut.quality_score ?? 3)
    setMeals(todayNut.meals_count ?? 3)
    setWater(Number(todayNut.water_liters ?? 2))
  }, [todayNut?.id])

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
    nutritionAvgQ.refetch()
  }

  useEffect(() => { setGoalInput(goal ?? '') }, [goal])

  // La meta antes vivía en el navegador: si quedó una ahí y el backend no tiene, se sube una vez
  useEffect(() => {
    if (!goalQ.data || goal !== null) return
    const old = Number(localStorage.getItem('lifeos.weight.goal'))
    if (!(old > 0)) return
    saveWeightGoal(old)
      .then(() => { localStorage.removeItem('lifeos.weight.goal'); goalQ.refetch() })
      .catch(() => {}) // se reintenta la próxima vez que se abra Peso
  }, [goalQ.data])

  async function saveGoal() {
    const value = goalInput === '' ? null : Number(goalInput)
    if (value === goal) return
    try {
      await saveWeightGoal(value)
      goalQ.refetch()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  const chartData = useMemo(
    () => (weightQ.data || []).map((w) => ({ date: w.date, weight: Number(w.weight_kg) })),
    [weightQ.data]
  )

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
                <CartesianGrid stroke="#1A201E" vertical={false} />
                <XAxis dataKey="date" stroke="#8C948F" fontSize={10} />
                <YAxis stroke="#8C948F" fontSize={10} domain={['dataMin - 1', 'dataMax + 1']} />
                <Tooltip
                  contentStyle={{ background: '#0F1312', border: '1px solid #1F2623', borderRadius: 8 }}
                />
                {goal !== null && (
                  <ReferenceLine y={goal} stroke="#2EBD85" strokeDasharray="4 4" label={{ value: `Meta ${goal}kg`, position: 'right', fill: '#2EBD85', fontSize: 10 }} />
                )}
                <Line type="monotone" dataKey="weight" stroke="#7C5CFF" strokeWidth={2.5} dot={{ r: 3, fill: '#7C5CFF' }} />
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
            value={goalInput} onChange={(e) => setGoalInput(e.target.value)}
            onBlur={saveGoal} onKeyDown={(e) => e.key === 'Enter' && e.target.blur()}
            placeholder="kg"
          />
        </div>
      </Card>

      <Card title="Nutrición de hoy" subtitle={`Promedio 7d: ${nutritionAvgQ.data?.avg_quality ?? '–'}/5`}>
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
