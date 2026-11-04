export default function Tabs({ items, value, onChange, className = '' }) {
  return (
    <div className={`inline-flex p-1 gap-0.5 rounded-xl bg-ink-900 border border-ink-700 ${className}`}>
      {items.map((it) => (
        <button
          key={it.value}
          onClick={() => onChange(it.value)}
          aria-pressed={value === it.value}
          className={`px-3.5 py-1.5 text-xs sm:text-sm font-semibold rounded-lg transition-colors duration-200 ${
            value === it.value ? 'bg-ink-700 text-ink-100' : 'text-ink-400 hover:text-ink-100'
          }`}
        >
          {it.icon && <span className="mr-1">{it.icon}</span>}
          {it.label}
        </button>
      ))}
    </div>
  )
}
