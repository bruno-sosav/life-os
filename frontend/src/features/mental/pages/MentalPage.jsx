import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PageHeader from '../../../shared/components/ui/PageHeader.jsx'
import Tabs from '../../../shared/components/ui/Tabs.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { swap } from '../../../shared/lib/motion.js'
import { fetchLists } from '../api/listas.api.js'
import { fetchSkills, fetchSkillTypes } from '../api/skills.api.js'
import SkillsTab from '../components/SkillsTab.jsx'
import ListsTab from '../components/ListsTab.jsx'

const TABS = [
  { value: 'aprender', label: 'Aprender' },
  { value: 'listas', label: 'Listas' }
]

export default function MentalPage() {
  const [tab, setTab] = useState('aprender')
  const skillsQ = useAsync(() => fetchSkills(), [])
  const typesQ = useAsync(() => fetchSkillTypes(), [])
  const listsQ = useAsync(() => fetchLists(), [])

  function refreshSkills() { skillsQ.refetch(); typesQ.refetch() }

  return (
    <div>
      <PageHeader title="Mental" subtitle="Lo que aprendés y tus listas"
        actions={<Tabs items={TABS} value={tab} onChange={setTab} />} />
      <AnimatePresence mode="wait">
        <motion.div key={tab} {...swap}>
          {tab === 'aprender' && skillsQ.data && <SkillsTab skills={skillsQ.data} types={typesQ.data || []} onChanged={refreshSkills} />}
          {tab === 'listas' && listsQ.data && (
            <ListsTab lists={listsQ.data} setLists={listsQ.setData} onChanged={listsQ.refetch} onSkillCreated={refreshSkills} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
