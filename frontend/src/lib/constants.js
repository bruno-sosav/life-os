export const PRIORITY_COLORS = {
  alta: '#D85A30',
  media: '#7F77DD',
  baja: '#1D9E75'
}

export const STATUS_LABELS = {
  pendiente: 'Pendiente',
  en_progreso: 'En progreso',
  hecho: 'Hecho'
}

export const MOOD_ICONS = ['😞', '😕', '😐', '🙂', '😄']

// Etiquetas libres (categorías, etiquetas de ideas…): cada texto toma siempre el mismo color
const LABEL_COLORS = ['#7C5CFF', '#FF9F0A', '#2EBD85', '#BF5AF2', '#5AC8FA', '#F6465D', '#FFD60A']

export function colorFor(label) {
  let hash = 0
  for (const ch of label) hash = (hash * 31 + ch.codePointAt(0)) >>> 0
  return LABEL_COLORS[hash % LABEL_COLORS.length]
}
