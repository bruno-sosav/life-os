import { useState } from 'react'
import PageHeader from '../../../shared/components/ui/PageHeader.jsx'
import Tabs from '../../../shared/components/ui/Tabs.jsx'
import Books from '../components/Books.jsx'
import Journal from '../components/Journal.jsx'
import MentalIdeas from '../components/MentalIdeas.jsx'
import MoodTracker from '../components/MoodTracker.jsx'
import { useAsync } from '../../../shared/hooks/useAsync.js'
import { fetchLibrary } from '../api/libros.api.js'

const TABS = [
  { value: 'libros',  label: 'Libros',   icon: '📚' },
  { value: 'diario',  label: 'Diario',   icon: '📓' },
  { value: 'ideas',   label: 'Ideas',    icon: '💡' },
  { value: 'estado',  label: 'Estado',   icon: '📊' }
]

export default function Mental() {
  const [tab, setTab] = useState('libros')
  const libraryQ = useAsync(() => fetchLibrary(), [])

  return (
    <div>
      <PageHeader
        title="Mental"
       
        subtitle="Libros, diario, ideas y estado de ánimo"
        actions={<Tabs items={TABS} value={tab} onChange={setTab} />}
      />

      {tab === 'libros' && libraryQ.data && <Books library={libraryQ.data} onChange={libraryQ.refetch} />}
      {tab === 'diario' && <Journal />}
      {tab === 'ideas'  && <MentalIdeas />}
      {tab === 'estado' && <MoodTracker />}
    </div>
  )
}
