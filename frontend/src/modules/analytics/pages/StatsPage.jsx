import { useState } from 'react'
import PageHeader from '../../../components/PageHeader.jsx'
import { useAsync } from '../../../hooks/useAsync.js'
import { fetchAnalyticsSummary } from '../api/resumen.api.js'
import WeekCompliance from '../components/WeekCompliance.jsx'
import KpiGrid from '../components/KpiGrid.jsx'
import ComplianceCalendar from '../components/ComplianceCalendar.jsx'
import ComplianceHistory from '../components/ComplianceHistory.jsx'
import HabitsByWeek from '../components/HabitsByWeek.jsx'
import WeeklyProfile from '../components/WeeklyProfile.jsx'
import ActivityPie from '../components/ActivityPie.jsx'
import FinanceChart from '../components/FinanceChart.jsx'
import { MoodSleep, WeightChart } from '../components/BodyAndMind.jsx'

// Todos los números vienen calculados del backend: acá solo se dibujan
export default function StatsPage() {
  const [weekOffset, setWeekOffset] = useState(0)
  const summaryQ = useAsync(() => fetchAnalyticsSummary(weekOffset), [weekOffset])
  const s = summaryQ.data

  return (
    <div className="space-y-4">
      <PageHeader title="Stats" subtitle="Tu vida en números" />
      {!s ? (
        <div className="text-sm text-ink-400 mt-8 text-center">
          {summaryQ.error ? 'No se pudieron cargar los datos.' : 'Cargando…'}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
            <div className="lg:col-span-2 space-y-4">
              <WeekCompliance summary={s} weekOffset={weekOffset} onWeekOffset={setWeekOffset} />
              <KpiGrid kpis={s.kpis} />
            </div>
            <div className="lg:col-span-3">
              <ComplianceCalendar />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <ComplianceHistory history={s.compliance_history} />
            <HabitsByWeek habitsByWeek={s.habits_by_week} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <WeeklyProfile radar={s.radar} />
            <ActivityPie distribution={s.activity_distribution} />
          </div>

          <WeightChart series={s.weight_series} />
          <MoodSleep series={s.mood_series} />
          <FinanceChart months={s.finance_monthly} />
        </>
      )}
    </div>
  )
}
