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
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/80"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.98 }}
            transition={{ duration: 0.22, ease: 'easeOut' }}
            role="dialog" aria-modal="true" aria-label={title}
            className={`modal-surface w-full ${sizes[size]} overflow-hidden rounded-t-2xl sm:rounded-2xl`}
            onClick={(e) => e.stopPropagation()}
          >
            {title && (
              <div className="px-5 pt-5 pb-4 border-b border-ink-700 flex items-center justify-between">
                <h3 className="font-semibold text-base">{title}</h3>
                <button
                  onClick={onClose}
                  aria-label="Cerrar"
                  className="w-8 h-8 rounded-lg hover:bg-ink-700 grid place-items-center text-ink-400 hover:text-ink-100 transition text-sm"
                >✕</button>
              </div>
            )}
            <div className="p-5 max-h-[75vh] overflow-y-auto">{children}</div>
            {footer && (
              <div className="px-5 py-4 border-t border-ink-700">{footer}</div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
