import { Routes, Route } from 'react-router-dom'
import PageHeader from '../../components/PageHeader.jsx'
import ListsGrid from './ListsGrid.jsx'
import ListView from './ListView.jsx'

export default function Listas() {
  return (
    <Routes>
      <Route
        index
        element={
          <div>
            <PageHeader title="Listas" subtitle="Compras, viajes, películas y todo lo que se te ocurra" />
            <ListsGrid />
          </div>
        }
      />
      <Route path=":id" element={<ListView />} />
    </Routes>
  )
}
