import { AnimatePresence, motion } from 'framer-motion'
import { useToastStore } from '../../shared/store/toastStore.js'

const ICONS = { success: '✓', error: '✕', info: 'ℹ' }
const COLOR = { success: 'text-up', error: 'text-down', info: 'text-accent' }

export default function ToastContainer() {
  const { toasts, remove } = useToastStore()
  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            role="status"
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-xl border border-ink-600 bg-ink-800 ${COLOR[t.type]}`}
          >
            <span className="w-5 h-5 rounded-full bg-ink-700 grid place-items-center text-[11px] font-bold shrink-0">
              {ICONS[t.type]}
            </span>
            <span className="text-sm font-medium text-ink-100 flex-1">{t.message}</span>
            <button
              onClick={() => remove(t.id)}
              aria-label="Cerrar aviso"
              className="text-ink-400 hover:text-ink-100 text-xs"
            >✕</button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
