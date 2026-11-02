// Tipos de campo que se pueden usar al armar una actividad (los valida el backend)
export const FIELD_TYPES = [
  { value: 'numero', label: 'Número' },
  { value: 'texto', label: 'Texto' },
  { value: 'si_no', label: 'Sí / No' },
  { value: 'opcion', label: 'Opción de lista' },
  { value: 'escala', label: 'Escala 1-5' },
  { value: 'ejercicios', label: 'Lista de ejercicios' }
]

export const CHARTABLE = ['numero', 'escala']

export const hasExercises = (activity) =>
  activity.fields.some((f) => f.type === 'ejercicios' && !f.archived)

// Cómo se muestra un valor guardado en el historial
export function formatValue(field, value) {
  if (field.type === 'si_no') return value ? 'Sí' : 'No'
  if (field.type === 'escala') return '★'.repeat(value)
  return field.unit ? `${value} ${field.unit}` : String(value)
}
