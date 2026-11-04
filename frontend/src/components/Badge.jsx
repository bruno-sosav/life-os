// Etiqueta de estado: texto de color sobre un fondo apenas teñido
export default function Badge({ children, color = '#8C948F' }) {
  return (
    <span className="chip" style={{ backgroundColor: `${color}14`, color }}>
      {children}
    </span>
  )
}
