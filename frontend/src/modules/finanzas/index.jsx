import { useState } from 'react'
import { format, startOfMonth, addMonths, subMonths } from 'date-fns'
import { es } from 'date-fns/locale'
import PageHeader from '../../components/PageHeader.jsx'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import EmptyState from '../../components/EmptyState.jsx'
import LabelPicker from '../../components/LabelPicker.jsx'
import { colorFor } from '../../lib/constants.js'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import {
  fetchMonthSummary, fetchLabels, fetchMonthIncome, createIncome, deleteIncome,
  fetchMonthExpenses, createExpense, deleteExpense
} from './queries.js'
import { fmt } from '../../lib/dates.js'
import {
  ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, Tooltip, XAxis, YAxis, CartesianGrid
} from 'recharts'


function fmt$ (n) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }).format(n)
}

export default function Finanzas() {
  const [refDate, setRefDate] = useState(new Date())
  const [addingIncome, setAddingIncome] = useState(false)
  const [addingExpense, setAddingExpense] = useState(false)

  const monthKey = format(refDate, 'yyyy-MM')
  const summaryQ = useAsync(() => fetchMonthSummary(refDate), [monthKey])
  const incomeQ = useAsync(() => fetchMonthIncome(refDate), [monthKey])
  const expensesQ = useAsync(() => fetchMonthExpenses(refDate), [monthKey])
  const labelsQ = useAsync(() => fetchLabels(), [])

  const income = incomeQ.data || []
  const expenses = expensesQ.data || []
  // Todos los totales vienen calculados del backend
  const summary = summaryQ.data || { income: 0, expenses: 0, savings: 0, savings_pct: null, spent_pct: null, by_category: [] }
  const labels = labelsQ.data || { expense_categories: [], income_sources: [] }

  const monthLabel = format(refDate, "MMMM yyyy", { locale: es }).replace(/^\w/, c => c.toUpperCase())

  function refetch() { summaryQ.refetch(); incomeQ.refetch(); expensesQ.refetch(); labelsQ.refetch() }

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
          <div className="text-lg font-bold text-[#30D158] mt-0.5 tabular-nums">{fmt$(summary.income)}</div>
        </Card>
        <Card>
          <div className="text-[11px] text-white/35">Gastos</div>
          <div className="text-lg font-bold text-[#FF453A] mt-0.5 tabular-nums">{fmt$(summary.expenses)}</div>
        </Card>
        <Card>
          <div className="text-[11px] text-white/35">Ahorro</div>
          <div className={`text-lg font-bold mt-0.5 tabular-nums ${summary.savings >= 0 ? 'text-[#0A84FF]' : 'text-[#FF453A]'}`}>{fmt$(summary.savings)}</div>
          {summary.savings_pct != null && <div className="text-[10px] text-white/30 mt-0.5">{summary.savings_pct}% del ingreso</div>}
        </Card>
      </div>

      {/* Savings bar */}
      {summary.spent_pct != null && (
        <div className="mb-4 px-1">
          <div className="flex justify-between text-[11px] text-white/35 mb-1">
            <span>Gastos sobre ingresos</span>
            <span>{summary.spent_pct}%</span>
          </div>
          <div className="h-2 bg-white/[0.07] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${summary.spent_pct}%`,
                background: summary.savings_pct >= 20 ? '#30D158' : summary.savings_pct >= 0 ? '#FF9F0A' : '#FF453A'
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
          {!summary.by_category.length ? (
            <EmptyState icon="🗂" title="Sin gastos" description="Agregá gastos para ver el desglose." />
          ) : (
            <div className="space-y-2">
              {summary.by_category.map((c) => (
                <div key={c.category}>
                  <div className="flex justify-between text-xs mb-0.5">
                    <span>{c.category}</span>
                    <span className="tabular-nums text-white/60">{fmt$(c.total)}</span>
                  </div>
                  <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${c.pct}%`, background: colorFor(c.category) }}
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
                return (
                  <li key={exp.id} className="py-2.5 flex items-center gap-3 group">
                    <span className="w-2 h-2 rounded-full shrink-0" style={{ background: colorFor(exp.category) }} />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-semibold">{exp.description || exp.category}</div>
                      <div className="text-xs text-white/35">{fmt(exp.date, "d 'de' MMM")} · {exp.category}</div>
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

      <IncomeModal open={addingIncome} onClose={() => setAddingIncome(false)} refDate={refDate} onSaved={refetch} sources={labels.income_sources} />
      <ExpenseModal open={addingExpense} onClose={() => setAddingExpense(false)} onSaved={refetch} categories={labels.expense_categories} />
    </div>
  )
}

function IncomeModal({ open, onClose, refDate, onSaved, sources }) {
  const [amount, setAmount] = useState('')
  const [source, setSource] = useState('')
  const [notes, setNotes] = useState('')

  async function save() {
    if (!amount || Number(amount) <= 0) return
    try {
      await createIncome({
        month: format(startOfMonth(refDate), 'yyyy-MM-dd'),
        amount: Number(amount),
        source: source.trim() || null,
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
        <LabelPicker id="income-source" label="Fuente (opcional)" value={source} options={sources}
          onChange={setSource} placeholder="Elegí una o escribí una nueva: Sueldo, Freelance…" />
        <div>
          <label className="label">Notas (opcional)</label>
          <input className="input" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="Sueldo enero, proyecto X…" />
        </div>
      </div>
    </Modal>
  )
}

function ExpenseModal({ open, onClose, onSaved, categories }) {
  const today = format(new Date(), 'yyyy-MM-dd')
  const [amount, setAmount] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(today)

  async function save() {
    if (!amount || Number(amount) <= 0) return
    if (!category.trim()) return toast.error('Elegí o escribí una categoría')
    try {
      await createExpense({
        date,
        amount: Number(amount),
        category: category.trim(),
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
        <LabelPicker id="expense-category" label="Categoría" value={category} options={categories}
          onChange={setCategory} placeholder="Elegí una o escribí una nueva: 🍔 Comida" />
        <div>
          <label className="label">Descripción (opcional)</label>
          <input className="input" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Almuerzo, nafta, Netflix…" />
        </div>
      </div>
    </Modal>
  )
}
