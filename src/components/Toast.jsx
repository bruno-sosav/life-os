import { AnimatePresence, motion } from 'framer-motion'
import { useToastStore } from '../store/toastStore.js'

const ICONS = { success: '✓', error: '✕', info: 'ℹ' }
const BG = {
  success: 'bg-[#30D158]/15 border-[#30D158]/30 text-[#30D158]',
  error: 'bg-[#FF453A]/15 border-[#FF453A]/30 text-[#FF453A]',
  info: 'bg-[#0A84FF]/15 border-[#0A84FF]/30 text-[#0A84FF]'
}

export default function ToastContainer() {
  const { toasts, remove } = useToastStore()
  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 max-w-sm w-full pointer-events-none">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div
            key={t.id}
            initial={{ opacity: 0, x: 40, scale: 0.9 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 40, scale: 0.9 }}
            transition={{ type: 'spring', stiffness: 400, damping: 30 }}
            className={`pointer-events-auto flex items-center gap-3 px-4 py-3 rounded-2xl border backdrop-blur-xl shadow-lg ${BG[t.type]}`}
          >
            <span className="w-5 h-5 rounded-full bg-current/20 grid place-items-center text-[11px] font-bold shrink-0">
              {ICONS[t.type]}
            </span>
            <span className="text-sm font-medium text-white/90 flex-1">{t.message}</span>
            <button
              onClick={() => remove(t.id)}
              className="text-white/40 hover:text-white/70 text-xs"
            >✕</button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
