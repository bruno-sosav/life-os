import { useMemo, useState } from 'react'
import { format, startOfMonth, addMonths, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchMonthIncome, createIncome, deleteIncome,
  fetchMonthExpenses, createExpense, deleteExpense
} from './queries.js'
import { fmt } from '../../lib/dates.js'
import {
  ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Tooltip, XAxis, YAxis, CartesianGrid
} from 'recharts'

const CATEGORIES = [
  { value: 'comida',       label: '🍔 Comida',       color: '#FF9F0A' },
  { value: 'transporte',   label: '🚗 Transporte',    color: '#0A84FF' },
  { value: 'salud',        label: '💊 Salud',          color: '#30D158' },
  { value: 'ocio',         label: '🎮 Ocio',           color: '#BF5AF2' },
  { value: 'ropa',         label: '👕 Ropa',           color: '#FF453A' },
  { value: 'educacion',    label: '📚 Educación',      color: '#5AC8FA' },
  { value: 'servicios',    label: '💡 Servicios',      color: '#FF9F0A' },
  { value: 'suscripciones',label: '📱 Suscripciones',  color: '#64D2FF' },
  { value: 'otro',         label: '📦 Otro',           color: '#8E8E93' },
]

const INCOME_SOURCES = ['sueldo', 'freelance', 'inversión', 'regalo', 'otro']

function fmt$ (n) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(n)
}

export default function Finanzas() {
  const [refDate, setRefDate] = useState(new Date())
  const [addingIncome, setAddingIncome] = useState(false)
  const [addingExpense, setAddingExpense] = useState(false)

  const incomeQ = useAsync(() => fetchMonthIncome(refDate), [format(refDate, 'yyyy-MM')])
  const expensesQ = useAsync(() => fetchMonthExpenses(refDate), [format(refDate, 'yyyy-MM')])

  const income = incomeQ.data || []
  const expenses = expensesQ.data || []

  const totalIncome = useMemo(() => income.reduce((s, i) => s + Number(i.amount), 0), [income])
  const totalExpenses = useMemo(() => expenses.reduce((s, e) => s + Number(e.amount), 0), [expenses])
  const savings = totalIncome - totalExpenses
  const savingsPct = totalIncome > 0 ? Math.round((savings / totalIncome) * 100) : 0

  const byCategory = useMemo(() => {
    const m = {}
    expenses.forEach((e) => {
      m[e.category] = (m[e.category] || 0) + Number(e.amount)
    })
    return CATEGORIES
      .filter((c) => m[c.value])
      .map((c) => ({ name: c.label, value: m[c.value], color: c.color }))
      .sort((a, b) => b.value - a.value)
  }, [expenses])

  const monthLabel = format(refDate, "MMMM yyyy", { locale: es }).replace(/^\w/, c => c.toUpperCase())

  function refetch() { incomeQ.refetch(); expensesQ.refetch() }

  return (
    <div>
      <PageHeader
        title="Finanzas"
       
        subtitle="Ingresos, gastos y ahorro"
        actions={
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => setRefDate(subMonths(refDate, 1))}>◀</Button>
            <span className="px-3 py-1.5 text-sm font-semibold text-white/70">{monthLabel}</span>
            <Button variant="ghost" size="sm" onClick={() => setRefDate(addMonths(refDate, 1))}>▶</Button>
          </div>
        }
      />

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <Card>
          <div className="text-[11px] text-white/35">Ingresos</div>
          <div className="text-lg font-bold text-[#30D158] mt-0.5 tabular-nums">{fmt$(totalIncome)}</div>
        </Card>
        <Card>
          <div className="text-[11px] text-white/35">Gastos</div>
          <div className="text-lg font-bold text-[#FF453A] mt-0.5 tabular-nums">{fmt$(totalExpenses)}</div>
        </Card>
        <Card>
          <div className="text-[11px] text-white/35">Ahorro</div>
          <div className={`text-lg font-bold mt-0.5 tabular-nums ${savings >= 0 ? 'text-[#0A84FF]' : 'text-[#FF453A]'}`}>{fmt$(savings)}</div>
          {totalIncome > 0 && <div className="text-[10px] text-white/30 mt-0.5">{savingsPct}% del ingreso</div>}
        </Card>
      </div>

      {/* Savings bar */}
      {totalIncome > 0 && (
        <div className="mb-4 px-1">
          <div className="flex justify-between text-[11px] text-white/35 mb-1">
            <span>Gastos sobre ingresos</span>
            <span>{Math.min(100, Math.round((totalExpenses / totalIncome) * 100))}%</span>
          </div>
          <div className="h-2 bg-white/[0.07] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (totalExpenses / totalIncome) * 100)}%`,
                background: savingsPct >= 20 ? '#30D158' : savingsPct >= 0 ? '#FF9F0A' : '#FF453A'
              }}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Ingresos */}
        <Card
          title="Ingresos"
         
          action={<Button size="sm" color="green" onClick={() => setAddingIncome(true)}>+ Ingreso</Button>}
        >
          {!income.length ? (
            <EmptyState icon="💵" title="Sin ingresos" description="Anotá lo que entra este mes." />
          ) : (
            <ul className="divide-y divide-white/[0.04]">
              {income.map((item) => (
                <li key={item.id} className="py-2.5 flex items-center gap-3 group">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold">{item.source || 'Ingreso'}</div>
                    {item.notes && <div className="text-xs text-white/35">{item.notes}</div>}
                  </div>
                  <span className="text-sm font-bold text-[#30D158] tabular-nums">{fmt$(item.amount)}</span>
                  <button
                    onClick={() => deleteIncome(item.id).then(() => { toast.success('Eliminado'); refetch() })}
                    className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs"
                  >✕</button>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Por categoría */}
        <Card title="Por categoría">
          {!byCategory.length ? (
            <EmptyState icon="🗂" title="Sin gastos" description="Agregá gastos para ver el desglose." />
          ) : (
            <div className="space-y-2">
              {byCategory.map((c) => (
                <div key={c.name}>
                  <div className="flex justify-between text-xs mb-0.5">
                    <span>{c.name}</span>
                    <span className="tabular-nums text-white/60">{fmt$(c.value)}</span>
                  </div>
                  <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${(c.value / totalExpenses) * 100}%`, background: c.color }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Gastos */}
        <Card
          title="Gastos"
         
          action={<Button size="sm" color="red" onClick={() => setAddingExpense(true)}>+ Gasto</Button>}
          className="lg:col-span-2"
        >
          {!expenses.length ? (
            <EmptyState icon="💸" title="Sin gastos" description="Registrá tus gastos del mes." />
          ) : (
            <ul className="divide-y divide-white/[0.04]">
              {expenses.map((exp) => {
                const cat = CATEGORIES.find((c) => c.value === exp.category)
                return (
                  <li key={exp.id} className="py-2.5 flex items-center gap-3 group">
                    <span className="text-base">{cat?.label.split(' ')[0] || '📦'}</span>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold">{exp.description || cat?.label.slice(3) || exp.category}</div>
                      <div className="text-xs text-white/35">{fmt(exp.date, "d 'de' MMM")} · {cat?.label.slice(3) || exp.category}</div>
                    </div>
                    <span className="text-sm font-bold text-[#FF453A] tabular-nums">{fmt$(exp.amount)}</span>
                    <button
                      onClick={() => deleteExpense(exp.id).then(() => { toast.success('Eliminado'); refetch() })}
                      className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs"
                    >✕</button>
                  </li>
                )
              })}
            </ul>
          )}
        </Card>
      </div>

      <IncomeModal open={addingIncome} onClose={() => setAddingIncome(false)} refDate={refDate} onSaved={refetch} />
      <ExpenseModal open={addingExpense} onClose={() => setAddingExpense(false)} onSaved={refetch} />
    </div>
  )
}

function IncomeModal({ open, onClose, refDate, onSaved }) {
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('sueldo')
  const [notes, setNotes] = useState('')

  async function save() {
    if (!amount || Number(amount) <= 0) return
    try {
      await createIncome({
        month: format(startOfMonth(refDate), 'yyyy-MM-dd'),
        amount: Number(amount),
        source,
        notes: notes.trim() || null
      })
      toast.success('Ingreso guardado ✓')
      setAmount(''); setNotes(''); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo ingreso"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button color="green" onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div>
          <label className="label">Monto ($)</label>
          <input type="number" min={0} className="input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="50000" />
        </div>
        <div>
          <label className="label">Fuente</label>
          <div className="flex gap-2 flex-wrap">
            {INCOME_SOURCES.map((s) => (
              <button key={s} type="button" onClick={() => setSource(s)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition capitalize ${source === s ? 'bg-[#30D158] text-white' : 'bg-white/[0.07] text-white/50'}`}>
                {s}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Notas (opcional)</label>
          <input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Sueldo enero, proyecto X…" />
        </div>
      </div>
    </Modal>
  )
}

function ExpenseModal({ open, onClose, onSaved }) {
  const today = format(new Date(), 'yyyy-MM-dd')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('comida')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(today)

  async function save() {
    if (!amount || Number(amount) <= 0) return
    try {
      await createExpense({
        date,
        amount: Number(amount),
        category,
        description: description.trim() || null
      })
      toast.success('Gasto guardado ✓')
      setAmount(''); setDescription(''); setDate(today); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nuevo gasto"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button color="red" onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Monto ($)</label>
            <input type="number" min={0} className="input" value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="1500" />
          </div>
          <div>
            <label className="label">Fecha</label>
            <input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} />
          </div>
        </div>
        <div>
          <label className="label">Categoría</label>
          <div className="grid grid-cols-3 gap-1.5">
            {CATEGORIES.map((c) => (
              <button key={c.value} type="button" onClick={() => setCategory(c.value)}
                className={`py-2 rounded-xl text-xs font-semibold transition ${category === c.value ? 'text-white' : 'bg-white/[0.06] text-white/40'}`}
                style={category === c.value ? { background: `${c.color}33`, border: `1px solid ${c.color}50`, color: c.color } : {}}>
                {c.label}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="label">Descripción (opcional)</label>
          <input className="input" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Almuerzo, nafta, Netflix…" />
        </div>
      </div>
    </Modal>
  )
}
