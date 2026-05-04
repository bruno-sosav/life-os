import { useEffect, useRef } from 'react'

const ITEM_H = 40

export default function DrumPicker({ values, selected, onChange, label, width = 72 }) {
  const ref = useRef(null)
  const idx = values.indexOf(selected)

  // Scroll to selected on mount and when selected changes
  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.scrollTo({ top: idx * ITEM_H, behavior: 'smooth' })
  }, [idx])

  function onScroll() {
    const el = ref.current
    if (!el) return
    const i = Math.round(el.scrollTop / ITEM_H)
    const clamped = Math.max(0, Math.min(values.length - 1, i))
    if (values[clamped] !== selected) onChange(values[clamped])
  }

  return (
    <div className="flex flex-col items-center gap-1" style={{ width }}>
      {label && <span className="text-[10px] uppercase tracking-wider text-white/30">{label}</span>}
      <div className="relative" style={{ width, height: ITEM_H * 3 }}>
        {/* Selection highlight */}
        <div
          className="absolute inset-x-0 rounded-xl pointer-events-none z-10"
          style={{ top: ITEM_H, height: ITEM_H, background: 'rgba(255,255,255,0.09)', border: '1px solid rgba(255,255,255,0.12)' }}
        />
        {/* Fade top */}
        <div className="absolute inset-x-0 top-0 h-10 pointer-events-none z-10" style={{ background: 'linear-gradient(to bottom, rgba(10,10,15,0.9), transparent)' }} />
        {/* Fade bottom */}
        <div className="absolute inset-x-0 bottom-0 h-10 pointer-events-none z-10" style={{ background: 'linear-gradient(to top, rgba(10,10,15,0.9), transparent)' }} />
        {/* Scroll container */}
        <div
          ref={ref}
          onScroll={onScroll}
          className="absolute inset-0 overflow-y-scroll"
          style={{
            scrollSnapType: 'y mandatory',
            WebkitOverflowScrolling: 'touch',
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
          }}
        >
          <style>{`.drum-no-scrollbar::-webkit-scrollbar{display:none}`}</style>
          {/* Padding items top */}
          <div style={{ height: ITEM_H }} />
          {values.map((v, i) => (
            <div
              key={v}
              onClick={() => {
                onChange(v)
                ref.current?.scrollTo({ top: i * ITEM_H, behavior: 'smooth' })
              }}
              style={{ height: ITEM_H, scrollSnapAlign: 'center' }}
              className="flex items-center justify-center text-lg font-semibold cursor-pointer select-none"
            >
              <span style={{ color: v === selected ? 'rgba(255,255,255,0.95)' : 'rgba(255,255,255,0.25)', transition: 'color 0.15s' }}>
                {String(v).padStart(2, '0')}
              </span>
            </div>
          ))}
          {/* Padding items bottom */}
          <div style={{ height: ITEM_H }} />
        </div>
      </div>
    </div>
  )
}
