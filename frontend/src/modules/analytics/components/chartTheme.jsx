// Estilo común de los gráficos de Stats: grilla y ejes discretos, tooltips con la paleta ink.
// Los textos van en colores de texto, nunca en el color de la serie.

export const INK = { grid: '#1A201E', axis: '#8C948F', text: '#E8ECE9', surface: '#0F1312', border: '#1F2623' }

export const AXIS = { stroke: INK.grid, tick: { fill: INK.axis, fontSize: 11 }, tickLine: false, axisLine: false }

export const GRID = { stroke: INK.grid, vertical: false }

export const TOOLTIP = {
  contentStyle: { background: INK.surface, border: `1px solid ${INK.border}`, borderRadius: 10, fontSize: 12 },
  labelStyle: { color: INK.axis, marginBottom: 4 },
  itemStyle: { color: INK.text },
  cursor: { fill: 'rgba(255,255,255,0.03)', stroke: INK.border }
}

export const LEGEND = {
  wrapperStyle: { fontSize: 11, paddingTop: 6 },
  formatter: (value) => <span style={{ color: '#C9CFCB' }}>{value}</span>
}
