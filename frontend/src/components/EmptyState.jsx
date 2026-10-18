export default function EmptyState({ icon = '✨', title, description, action }) {
  return (
    <div className="text-center py-12 px-4">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="font-display font-bold text-base mb-1">{title}</h3>
      {description && <p className="text-sm text-white/40 max-w-xs mx-auto">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
