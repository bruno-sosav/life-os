import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar.jsx'
import BottomNav from './BottomNav.jsx'
import ToastContainer from './Toast.jsx'
import { motion } from 'framer-motion'

export default function Layout() {
  return (
    <div className="flex min-h-screen" style={{ background: '#0a0a0f' }}>
      <Sidebar />
      <main className="flex-1 min-w-0 pb-24 md:pb-0 md:pl-56">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2, ease: 'easeOut' }}
          className="mx-auto w-full max-w-6xl px-4 sm:px-6 py-6"
        >
          <Outlet />
        </motion.div>
      </main>
      <BottomNav />
      <ToastContainer />
    </div>
  )
}
