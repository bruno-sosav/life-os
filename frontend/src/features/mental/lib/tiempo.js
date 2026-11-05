// "2 h 15 min", "45 min", "3 h"
export function hm(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (!h) return `${m} min`
  return m ? `${h} h ${m} min` : `${h} h`
}

export const STAGES = [
  { value: 'practicando', label: 'Practicando', tone: 'text-up' },
  { value: 'en_pausa', label: 'En pausa', tone: 'text-ink-400' },
  { value: 'la_tengo', label: 'Ya la tengo', tone: 'text-accent' }
]

export const stageOf = (value) => STAGES.find((s) => s.value === value) ?? STAGES[0]
