export default function Badge({ children, color = 'rgba(255,255,255,0.4)' }) {
  return (
    <span
      className="chip font-semibold"
      style={{
        backgroundColor: `${color}1a`,
        color,
        border: `1px solid ${color}33`
      }}
    >
      {children}
    </span>
  )
}
