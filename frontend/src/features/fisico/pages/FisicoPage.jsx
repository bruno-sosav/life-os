import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PageHeader from '../../../shared/components/ui/PageHeader.jsx'
import Tabs from '../../../shared/components/ui/Tabs.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { swap } from '../../../shared/lib/motion.js'
import { fetchActivities } from '../api/actividades.api.js'
import TrainingTab from '../components/TrainingTab.jsx'
import PesoNutricion from '../components/PesoNutricion.jsx'

const TABS = [
  { value: 'entrenamiento', label: 'Entrenamiento' },
  { value: 'peso', label: 'Peso y nutrición' }
]

export default function FisicoPage() {
  const [tab, setTab] = useState('entrenamiento')
  const activitiesQ = useAsync(() => fetchActivities(), [])

  return (
    <div>
      <PageHeader title="Físico" subtitle="Tus entrenamientos, peso y nutrición" actions={<Tabs items={TABS} value={tab} onChange={setTab} />} />
      <AnimatePresence mode="wait">
        <motion.div key={tab} {...swap}>
          {tab === 'peso' ? (
            <PesoNutricion />
          ) : (
            activitiesQ.data && <TrainingTab activities={activitiesQ.data} onActivitiesChanged={activitiesQ.refetch} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
