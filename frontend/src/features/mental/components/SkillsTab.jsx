import { useState } from 'react'
import { motion } from 'framer-motion'
import Button from '../../../shared/components/ui/Button.jsx'
import EmptyState from '../../../shared/components/ui/EmptyState.jsx'
import { item, list } from '../../../shared/lib/motion.js'
import { hm } from '../lib/tiempo.js'
import SkillCard from './SkillCard.jsx'
import SkillModal from './SkillModal.jsx'
import PracticeModal from './PracticeModal.jsx'

// Aprender: las skills con su semana, registrar práctica y crear o editar skills
export default function SkillsTab({ skills, types, onChanged }) {
  const [open, setOpen] = useState(null)
  const [editing, setEditing] = useState(null) // null = cerrado, {} = nueva, skill = editar
  const [practicing, setPracticing] = useState(false)
  const practicable = skills.filter((s) => s.stage !== 'la_tengo')
  const week = skills.reduce((sum, s) => sum + s.week_minutes, 0)

  return (
    <div className="space-y-4">
      <div className="card-pad flex items-center justify-between gap-4">
        <div>
          <div className="text-[11px] text-ink-400 font-medium">Practicado esta semana</div>
          <div className="font-mono text-3xl font-bold text-up mt-0.5">{hm(week)}</div>
        </div>
        <div className="flex flex-col sm:flex-row gap-2">
          <Button onClick={() => setPracticing(true)} disabled={!practicable.length}>+ Registrar práctica</Button>
          <Button variant="secondary" onClick={() => setEditing({})}>+ Skill</Button>
        </div>
      </div>

      {!skills.length ? (
        <div className="card-pad">
          <EmptyState icon="+" title="Sin skills todavía" description="Anotá lo que querés aprender: ajedrez, un idioma, ventas… o pasalo desde una lista." />
        </div>
      ) : (
        <motion.div variants={list} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 gap-3 items-start">
          {skills.map((s) => (
            <motion.div key={s.id} variants={item}>
              <SkillCard skill={s} open={open === s.id} onToggle={() => setOpen(open === s.id ? null : s.id)}
                onEdit={() => setEditing(s)} onChanged={onChanged} />
            </motion.div>
          ))}
        </motion.div>
      )}

      <SkillModal skill={editing} types={types} onClose={() => setEditing(null)} onSaved={onChanged} />
      <PracticeModal open={practicing} skills={practicable} initialSkill={open}
        onClose={() => setPracticing(false)} onSaved={(id) => { setOpen(id); onChanged() }} />
    </div>
  )
}
