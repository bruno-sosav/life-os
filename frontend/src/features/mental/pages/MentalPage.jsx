import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import PageHeader from '../../../shared/components/ui/PageHeader.jsx'
import Tabs from '../../../shared/components/ui/Tabs.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { swap } from '../../../shared/lib/motion.js'
import { fetchLibrary } from '../api/libros.api.js'
import { fetchLists } from '../api/listas.api.js'
import { fetchSkills, fetchSkillTypes } from '../api/skills.api.js'
import SkillsTab from '../components/SkillsTab.jsx'
import ListsTab from '../components/ListsTab.jsx'
import Books from '../components/Books.jsx'
import MentalIdeas from '../components/MentalIdeas.jsx'

const TABS = [
  { value: 'aprender', label: 'Aprender' },
  { value: 'listas', label: 'Listas' },
  { value: 'libros', label: 'Libros' },
  { value: 'ideas', label: 'Ideas' }
]

export default function MentalPage() {
  const [tab, setTab] = useState('aprender')
  const skillsQ = useAsync(() => fetchSkills(), [])
  const typesQ = useAsync(() => fetchSkillTypes(), [])
  const listsQ = useAsync(() => fetchLists(), [])
  const libraryQ = useAsync(() => fetchLibrary(), [])
  const skills = skillsQ.data || []

  function refreshSkills() { skillsQ.refetch(); typesQ.refetch() }

  return (
    <div>
      <PageHeader title="Mental" subtitle="Lo que aprendés, tus listas, libros e ideas"
        actions={<Tabs items={TABS} value={tab} onChange={setTab} />} />
      <AnimatePresence mode="wait">
        <motion.div key={tab} {...swap}>
          {tab === 'aprender' && skillsQ.data && <SkillsTab skills={skills} types={typesQ.data || []} onChanged={refreshSkills} />}
          {tab === 'listas' && listsQ.data && (
            <ListsTab lists={listsQ.data} setLists={listsQ.setData} onChanged={listsQ.refetch} onSkillCreated={refreshSkills} />
          )}
          {tab === 'libros' && libraryQ.data && (
            <Books library={libraryQ.data} skills={skills} onChange={() => { libraryQ.refetch(); skillsQ.refetch() }} />
          )}
          {tab === 'ideas' && <MentalIdeas />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}
