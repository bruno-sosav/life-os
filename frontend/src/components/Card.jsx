export default function Card({ title, subtitle, action, className = '', children, emoji }) {
  return (
    <div className={`card-pad ${className}`}>
      {(title || action) && (
        <div className="flex items-start justify-between mb-4 gap-2">
          <div>
            {title && (
              <h3 className="font-display font-bold text-base leading-tight flex items-center gap-2">
                {emoji && <span>{emoji}</span>}
                {title}
              </h3>
            )}
            {subtitle && <p className="text-xs text-white/40 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="flex items-center gap-1.5 shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </div>
  )
}
