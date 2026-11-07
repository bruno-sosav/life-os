import { useEffect, useRef } from 'react'

const ITEM_H = 40

// Ruedita de valores (horas, minutos). Con el teclado: flechas arriba y abajo.
export default function DrumPicker({ values, selected, onChange, label, width = 72 }) {
  const ref = useRef(null)
  const settle = useRef(null)
  const idx = values.indexOf(selected)

  // Lleva el valor elegido al centro, al abrir y cada vez que cambia
  useEffect(() => {
    ref.current?.scrollTo({ top: idx * ITEM_H, behavior: 'smooth' })
  }, [idx])

  useEffect(() => () => clearTimeout(settle.current), [])

  // Elige recién cuando el scroll se detiene: durante la animación pasaría por valores intermedios
  function onScroll() {
    clearTimeout(settle.current)
    settle.current = setTimeout(() => {
      const i = Math.round(ref.current.scrollTop / ITEM_H)
      const value = values[Math.max(0, Math.min(values.length - 1, i))]
      if (value !== selected) onChange(value)
    }, 120)
  }

  function onKeyDown(e) {
    const step = { ArrowUp: -1, ArrowDown: 1 }[e.key]
    if (!step) return
    e.preventDefault()
    const next = values[idx + step]
    if (next !== undefined) onChange(next)
  }

  return (
    <div className="flex flex-col items-center gap-1" style={{ width }}>
      {label && <span className="text-[10px] uppercase tracking-wider text-ink-400">{label}</span>}
      <div className="relative" style={{ width, height: ITEM_H * 3 }}>
        <div className="absolute inset-x-0 rounded-xl pointer-events-none z-10 bg-ink-100/[0.06] border border-ink-600"
          style={{ top: ITEM_H, height: ITEM_H }} />
        <div className="absolute inset-x-0 top-0 h-10 pointer-events-none z-10 bg-gradient-to-b from-ink-800 to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-10 pointer-events-none z-10 bg-gradient-to-t from-ink-800 to-transparent" />
        <div
          ref={ref}
          onScroll={onScroll}
          onKeyDown={onKeyDown}
          tabIndex={0}
          role="spinbutton"
          aria-label={label}
          aria-valuenow={selected}
          aria-valuetext={String(selected).padStart(2, '0')}
          className="absolute inset-0 overflow-y-scroll no-scrollbar rounded-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-accent"
          style={{ scrollSnapType: 'y mandatory', scrollbarWidth: 'none' }}
        >
          <div style={{ height: ITEM_H }} />
          {values.map((v) => (
            <div key={v} onClick={() => onChange(v)} style={{ height: ITEM_H, scrollSnapAlign: 'center' }}
              className={`flex items-center justify-center font-mono text-lg font-semibold cursor-pointer select-none transition-colors ${
                v === selected ? 'text-ink-100' : 'text-ink-500'
              }`}>
              {String(v).padStart(2, '0')}
            </div>
          ))}
          <div style={{ height: ITEM_H }} />
        </div>
      </div>
    </div>
  )
}
