export const CATEGORY_COLORS = {
  gym: '#D85A30',
  mma: '#E33E3E',
  estudio: '#3D8BFF',
  negocio: '#7F77DD',
  personal: '#1D9E75',
  default: '#5b5b68'
}


export const HOURS = Array.from({ length: 18 }, (_, i) => i + 6) // 6am → 23

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
const LABEL_COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#5AC8FA', '#FF453A', '#FFD60A']

export function colorFor(label) {
  let hash = 0
  for (const ch of label) hash = (hash * 31 + ch.codePointAt(0)) >>> 0
  return LABEL_COLORS[hash % LABEL_COLORS.length]
}
