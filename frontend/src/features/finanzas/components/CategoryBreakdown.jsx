import { motion } from 'framer-motion'
import Card from '../../../shared/components/ui/Card.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { colorFor } from '../../../shared/lib/constants.js'
import { item, list } from '../../../shared/lib/motion.js'
import { money } from '../lib/dinero.js'

// En qué se fue la plata, de la categoría más grande a la más chica
export default function CategoryBreakdown({ categories }) {
  return (
    <Card title="Por categoría">
      {!categories.length ? (
        <EmptyState icon="—" title="Sin gastos" description="Cargá gastos para ver el desglose." />
      ) : (
        <motion.ul variants={list} initial="hidden" animate="show" className="space-y-3">
          {categories.map((c) => (
            <motion.li key={c.category} variants={item}>
              <div className="flex items-baseline justify-between text-sm mb-1">
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: colorFor(c.category) }} />
                  {c.category}
                </span>
                <span className="font-mono text-ink-300">
                  {money(c.total)} <span className="text-ink-400 text-xs">· {c.pct}%</span>
                </span>
              </div>
              <div className="h-1.5 bg-ink-700 rounded-full overflow-hidden" aria-hidden="true">
                <motion.div className="h-full rounded-full" style={{ background: colorFor(c.category) }}
                  initial={{ width: 0 }} animate={{ width: `${c.pct}%` }} transition={{ duration: 0.6, ease: [0.2, 0.8, 0.2, 1] }} />
              </div>
            </motion.li>
          ))}
        </motion.ul>
      )}
    </Card>
  )
}
