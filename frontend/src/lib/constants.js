// La prioridad se muestra como texto de color (ya no ordena: el orden del tablero es manual)
export const PRIORITY_COLORS = {
  alta: '#F6465D',
  media: '#E0B84A',
  baja: '#8C948F'
}

export const STATUS_LABELS = {
  pendiente: 'Pendiente',
  en_progreso: 'En proceso',
  hecho: 'Finalizado'
}

export const MOOD_ICONS = ['😞', '😕', '😐', '🙂', '😄']

// Etiquetas libres (categorías, etiquetas de ideas…): cada texto toma siempre el mismo color
const LABEL_COLORS = ['#7C5CFF', '#FF9F0A', '#2EBD85', '#BF5AF2', '#5AC8FA', '#F6465D', '#FFD60A']

export function colorFor(label) {
  let hash = 0
  for (const ch of label) hash = (hash * 31 + ch.codePointAt(0)) >>> 0
  return LABEL_COLORS[hash % LABEL_COLORS.length]
}
