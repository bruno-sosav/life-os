import { useState } from 'react'
import PageHeader from '../../components/PageHeader.jsx'
import Tabs from '../../components/Tabs.jsx'
import Books from './Books.jsx'
import Journal from './Journal.jsx'
import MentalIdeas from './MentalIdeas.jsx'
import MoodTracker from './MoodTracker.jsx'
import { useAsync } from '../../hooks/useAsync.js'
import { fetchBooks } from './queries.js'

const TABS = [
  { value: 'libros',  label: 'Libros',   icon: '📚' },
  { value: 'diario',  label: 'Diario',   icon: '📓' },
  { value: 'ideas',   label: 'Ideas',    icon: '💡' },
  { value: 'estado',  label: 'Estado',   icon: '📊' }
]

export default function Mental() {
  const [tab, setTab] = useState('libros')
  const booksQ = useAsync(() => fetchBooks(), [])

  return (
    <div>
      <PageHeader
        title="Mental"
        emoji="🧠"
        subtitle="Libros, diario, ideas y estado de ánimo"
        actions={<Tabs items={TABS} value={tab} onChange={setTab} />}
      />

      {tab === 'libros' && <Books books={booksQ.data || []} onChange={booksQ.refetch} />}
      {tab === 'diario' && <Journal />}
      {tab === 'ideas'  && <MentalIdeas />}
      {tab === 'estado' && <MoodTracker />}
    </div>
  )
}
