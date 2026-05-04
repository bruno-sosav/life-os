export default function PageHeader({ title, subtitle, actions, emoji }) {
  return (
    <div className="mb-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-2xl sm:text-3xl font-bold tracking-tight flex items-center gap-2">
            {emoji && <span className="text-2xl">{emoji}</span>}
            {title}
          </h1>
          {subtitle && <p className="text-sm text-white/40 mt-1">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  )
}
