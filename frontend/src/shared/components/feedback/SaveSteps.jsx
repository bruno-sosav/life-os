import { motion } from 'framer-motion'

// Lo que muestra un formulario mientras guarda y cuando terminó (como un "procesando pago")
export default function SaveSteps({ step, savingText = 'Guardando…', doneTitle, doneText }) {
  if (step === 'saving') {
    return (
      <motion.div key="saving" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
        role="status" className="py-8 flex flex-col items-center gap-3">
        <svg className="animate-spin" width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="12" cy="12" r="10" stroke="#1F2623" strokeWidth="2.5" />
          <path d="M22 12a10 10 0 0 0-10-10" stroke="#2EBD85" strokeWidth="2.5" strokeLinecap="round" />
        </svg>
        <span className="text-sm text-ink-400">{savingText}</span>
      </motion.div>
    )
  }
  return (
    <motion.div key="done" initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
      role="status" className="py-4 flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <motion.span initial={{ scale: 0.6 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 500, damping: 22 }}
          className="w-8 h-8 rounded-full bg-up/15 grid place-items-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2EBD85" strokeWidth="3" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
        </motion.span>
        <span className="text-base font-semibold">{doneTitle}</span>
      </div>
      {doneText && <p className="text-sm text-ink-400">{doneText}</p>}
    </motion.div>
  )
}
