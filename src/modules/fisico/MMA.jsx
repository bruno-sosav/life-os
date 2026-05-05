import { useMemo, useState } from 'react'
import Card from '../../components/Card.jsx'
import Button from '../../components/Button.jsx'
import Modal from '../../components/Modal.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { toast } from '../../store/toastStore.js'
import { fetchMMASessions, createMMASession, deleteMMASession } from './queries.js'
import { fetchLinkedModuleHabit, fetchHabitLogsRange, toggleHabitLog } from '../dashboard/queries.js'
import { fmt, monthRange, todayISO, isSameDay, format, weekRange, eachDayOfInterval } from '../../lib/dates.js'

const TYPES = ['técnica', 'sparring', 'grappling', 'libre']
const DOW = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

export default function MMA() {
  const sessionsQ = useAsync(() => fetchMMASessions(), [])
  const [adding, setAdding] = useState(false)
  const [refDate, setRefDate] = useState(new Date())

  // Hábito vinculado al módulo mma (sync con dashboard)
  const mmaHabitQ = useAsync(() => fetchLinkedModuleHabit('mma'), [])
  const mmaHabit = mmaHabitQ.data

  const { days: monthDays, start } = monthRange(refDate)
  const { start: wStart, end: wEnd } = weekRange()
  const weekDays = eachDayOfInterval({ start: wStart, end: wEnd })
  const startISO = format(wStart, 'yyyy-MM-dd')
  const endISO = format(wEnd, 'yyyy-MM-dd')

  const weekHabitLogsQ = useAsync(
    () => mmaHabit ? fetchHabitLogsRange(startISO, endISO) : Promise.resolve([]),
    [mmaHabit?.id, startISO, endISO]
  )

  const sessionsByDate = useMemo(() => {
    const m = {}
    ;(sessionsQ.data || []).forEach((s) => { m[s.date] = s })
    return m
  }, [sessionsQ.data])

  const attendedDates = useMemo(() => {
    const s = new Set()
    if (mmaHabit) {
      ;(weekHabitLogsQ.data || [])
        .filter((l) => l.habit_id === mmaHabit.id && l.completed)
        .forEach((l) => s.add(l.date))
    } else {
      ;(sessionsQ.data || []).filter((sess) => sess.attended).forEach((sess) => s.add(sess.date))
    }
    return s
  }, [mmaHabit, weekHabitLogsQ.data, sessionsQ.data])

  const monthSessions = useMemo(() => {
    const mStart = start.toISOString().slice(0, 10)
    return (sessionsQ.data || []).filter((s) => s.date >= mStart && s.date <= monthDays[monthDays.length - 1].toISOString().slice(0, 10))
  }, [sessionsQ.data, start, monthDays])

  async function quickToggle(dateISO) {
    try {
      if (mmaHabit) {
        const log = (weekHabitLogsQ.data || []).find((l) => l.date === dateISO && l.habit_id === mmaHabit.id)
        const next = !log?.completed
        await toggleHabitLog({ habit_id: mmaHabit.id, date: dateISO, completed: next })
        toast.success(next ? '¡MMA completado! ✓' : 'Desmarcado')
        weekHabitLogsQ.refetch()
      } else {
        const existing = sessionsByDate[dateISO]
        if (existing) {
          const { supabase } = await import('../../lib/supabase.js')
          const newAttended = !existing.attended
          const { error } = await supabase.from('mma_sessions').update({ attended: newAttended }).eq('id', existing.id)
          if (error) throw error
          toast.success(newAttended ? '¡Estuvo presente! ✓' : 'Desmarcado')
        } else {
          await createMMASession({ date: dateISO, attended: true, session_type: 'técnica' })
          toast.success('Sesión registrada ✓')
        }
        sessionsQ.refetch()
      }
    } catch (e) {
      toast.error('Error: ' + e.message)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div className="lg:col-span-2 space-y-4">
        {/* Weekly quick-check */}
        <Card
          title="Esta semana"
         
          subtitle={mmaHabit ? `Sincronizado con hábito "${mmaHabit.name}"` : 'Vincular hábito en Dashboard → + Hábito'}
        >
          <div className="grid grid-cols-7 gap-1.5">
            {weekDays.map((day, i) => {
              const iso = format(day, 'yyyy-MM-dd')
              const attended = attendedDates.has(iso)
              const isToday = iso === todayISO()
              return (
                <button
                  key={iso}
                  onClick={() => quickToggle(iso)}
                  className="flex flex-col items-center gap-1 py-3 rounded-[14px] transition-all active:scale-95"
                  style={{
                    background: attended ? '#30D15822' : 'rgba(255,255,255,0.04)',
                    border: `1px solid ${attended ? '#30D15840' : isToday ? 'rgba(10,132,255,0.5)' : 'rgba(255,255,255,0.06)'}`
                  }}
                >
                  <span className="text-[10px] font-semibold text-white/40">{DOW[i]}</span>
                  <span className="text-base">{attended ? '✓' : '○'}</span>
                  <span className="text-[10px] font-bold" style={{ color: attended ? '#30D158' : isToday ? '#0A84FF' : 'rgba(255,255,255,0.25)' }}>{day.getDate()}</span>
                </button>
              )
            })}
          </div>
        </Card>

        {/* Monthly calendar */}
        <Card
          title={fmt(refDate, "MMMM yyyy").replace(/^\w/, c => c.toUpperCase())}
          subtitle={`${monthSessions.length} clases este mes`}
          action={
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" onClick={() => { const d = new Date(refDate); d.setMonth(d.getMonth() - 1); setRefDate(d) }}>◀</Button>
              <Button variant="ghost" size="sm" onClick={() => { const d = new Date(refDate); d.setMonth(d.getMonth() + 1); setRefDate(d) }}>▶</Button>
              <Button size="sm" onClick={() => setAdding(true)}>+ Sesión</Button>
            </div>
          }
        >
          <div className="grid grid-cols-7 gap-1">
            {['L','M','M','J','V','S','D'].map((d, i) => <div key={i} className="text-[10px] text-center text-white/30 uppercase py-1">{d}</div>)}
            {Array.from({ length: (monthDays[0].getDay() + 6) % 7 }).map((_, i) => <div key={`o${i}`} />)}
            {monthDays.map((d) => {
              const iso = format(d, 'yyyy-MM-dd')
              const session = sessionsByDate[iso]
              const isToday = isSameDay(d, new Date())
              return (
                <button
                  key={iso}
                  onClick={() => quickToggle(iso)}
                  className="aspect-square rounded-xl text-[11px] grid place-items-center transition"
                  style={{
                    background: session?.attended ? '#30D15820' : session ? '#FF453A15' : isToday ? '#0A84FF15' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${isToday ? '#0A84FF50' : 'transparent'}`,
                    color: session?.attended ? '#30D158' : session ? '#FF453A' : isToday ? '#0A84FF' : 'rgba(255,255,255,0.5)',
                    fontWeight: (session || isToday) ? 700 : 400
                  }}
                >
                  {d.getDate()}
                </button>
              )
            })}
          </div>
        </Card>
      </div>

      <Card title="Recientes">
        <ul className="divide-y divide-white/[0.04]">
          {(sessionsQ.data || []).slice(0, 10).map((s) => (
            <li key={s.id} className="py-2.5 flex items-center gap-2 group">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: s.attended ? '#30D158' : '#FF453A' }} />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium">{s.session_type || 'Sesión'}</div>
                <div className="text-[11px] text-white/35">{fmt(s.date, 'd MMM')}</div>
              </div>
              <button onClick={() => deleteMMASession(s.id).then(() => { toast.success('Eliminado'); sessionsQ.refetch() })}
                className="opacity-0 group-hover:opacity-100 text-white/25 hover:text-[#FF453A] text-xs">✕</button>
            </li>
          ))}
          {!(sessionsQ.data || []).length && <li className="py-4 text-center text-xs text-white/30">Sin sesiones</li>}
        </ul>
      </Card>

      <NewMMAModal open={adding} onClose={() => setAdding(false)} onSaved={() => sessionsQ.refetch()} />
    </div>
  )
}

function NewMMAModal({ open, onClose, onSaved }) {
  const [date, setDate] = useState(todayISO())
  const [type, setType] = useState('técnica')
  const [notes, setNotes] = useState('')

  async function save() {
    try {
      await createMMASession({ date, session_type: type, attended: true, notes: notes.trim() || null })
      toast.success('Sesión guardada ✓')
      setNotes(''); onSaved(); onClose()
    } catch (e) { toast.error('Error: ' + e.message) }
  }

  return (
    <Modal open={open} onClose={onClose} title="Nueva sesión de MMA"
      footer={<div className="flex justify-end gap-2"><Button variant="ghost" onClick={onClose}>Cancelar</Button><Button onClick={save}>Guardar</Button></div>}
    >
      <div className="space-y-3">
        <div className="grid grid-cols-2 gap-3">
          <div><label className="label">Fecha</label><input type="date" className="input" value={date} onChange={(e) => setDate(e.target.value)} /></div>
          <div>
            <label className="label">Tipo</label>
            <select className="input" value={type} onChange={(e) => setType(e.target.value)}>
              {TYPES.map((t) => <option key={t}>{t}</option>)}
            </select>
          </div>
        </div>
        <div><label className="label">Notas</label><textarea className="input min-h-[80px]" value={notes} onChange={(e) => setNotes(e.target.value)} /></div>
      </div>
    </Modal>
  )
}
