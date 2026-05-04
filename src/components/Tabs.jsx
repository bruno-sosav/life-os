export default function Tabs({ items, value, onChange, className = '' }) {
  return (
    <div className={`inline-flex p-1 gap-0.5 rounded-xl ${className}`} style={{ background: 'rgba(255,255,255,0.06)' }}>
      {items.map((it) => (
        <button
          key={it.value}
          onClick={() => onChange(it.value)}
          className={`px-3.5 py-1.5 text-xs sm:text-sm font-semibold rounded-[10px] transition-all duration-200 ${
            value === it.value
              ? 'bg-white/[0.14] text-white shadow-sm'
              : 'text-white/45 hover:text-white/70'
          }`}
        >
          {it.icon && <span className="mr-1">{it.icon}</span>}
          {it.label}
        </button>
      ))}
    </div>
  )
}
