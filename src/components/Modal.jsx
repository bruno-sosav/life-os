import { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const sizes = { sm: 'max-w-sm', md: 'max-w-md', lg: 'max-w-2xl', xl: 'max-w-4xl' }

export default function Modal({ open, onClose, title, children, footer, size = 'md' }) {
  useEffect(() => {
    if (!open) return
    const fn = (e) => e.key === 'Escape' && onClose?.()
    window.addEventListener('keydown', fn)
    return () => window.removeEventListener('keydown', fn)
  }, [open, onClose])

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.98 }}
            transition={{ type: 'spring', stiffness: 420, damping: 32 }}
            className={`modal-surface w-full ${sizes[size]} overflow-hidden rounded-[24px]`}
            onClick={(e) => e.stopPropagation()}
          >
            {title && (
              <div className="px-5 pt-5 pb-4 border-b border-white/[0.06] flex items-center justify-between">
                <h3 className="font-display font-bold text-base">{title}</h3>
                <button
                  onClick={onClose}
                  className="w-7 h-7 rounded-full bg-white/[0.08] hover:bg-white/[0.14] grid place-items-center text-white/50 hover:text-white transition text-sm"
                >✕</button>
              </div>
            )}
            <div className="p-5 max-h-[75vh] overflow-y-auto">{children}</div>
            {footer && (
              <div className="px-5 py-4 border-t border-white/[0.06]">{footer}</div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
