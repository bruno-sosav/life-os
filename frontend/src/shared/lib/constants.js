// La prioridad se muestra como texto de color (ya no ordena: el orden del tablero es manual)
export const PRIORITY_COLORS = {
  alta: '#F6465D',
  media: '#E0B84A',
  baja: '#8C948F'
}

// Colores de identidad (proyectos, tipos de entrenamiento), en este orden. Validados para
// daltonismo sobre el fondo de las tarjetas; no se confunden con up/down/warn/accent.
export const PICK_COLORS = ['#3987E5', '#D95926', '#199E70', '#C98500', '#D55181', '#9085E9']

export const STATUS_LABELS = {
  pendiente: 'Pendiente',
  en_progreso: 'En proceso',
  hecho: 'Finalizado'
}


// Etiquetas libres (categorías, etiquetas de ideas…): cada texto toma siempre el mismo color
export function colorFor(label) {
  let hash = 0
  for (const ch of label) hash = (hash * 31 + ch.codePointAt(0)) >>> 0
  return PICK_COLORS[hash % PICK_COLORS.length]
}
