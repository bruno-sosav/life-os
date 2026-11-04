// Un input según el tipo de campo del tipo de entrenamiento. Un valor vacío no se guarda.
export default function FieldInput({ field, value, onChange }) {
  const id = `field-${field.id}`
  const label = <label className="label" htmlFor={id}>{field.name}{field.unit ? ` (${field.unit})` : ''}</label>

  if (field.type === 'numero') {
    return (
      <div>
        {label}
        <input id={id} type="number" step="any" className="input font-mono" value={value ?? ''}
          onChange={(e) => onChange(e.target.value === '' ? null : Number(e.target.value))} />
      </div>
    )
  }
  if (field.type === 'opcion') {
    return (
      <div>
        {label}
        <select id={id} className="input" value={value ?? ''} onChange={(e) => onChange(e.target.value || null)}>
          <option value="">—</option>
          {field.options.map((o) => <option key={o}>{o}</option>)}
        </select>
      </div>
    )
  }
  if (field.type === 'si_no' || field.type === 'escala') {
    const choices = field.type === 'si_no'
      ? [{ v: true, label: 'Sí' }, { v: false, label: 'No' }]
      : [1, 2, 3, 4, 5].map((n) => ({ v: n, label: String(n) }))
    return (
      <div>
        <span className="label" id={id}>{field.name}</span>
        <div className="flex gap-1.5" role="group" aria-labelledby={id}>
          {choices.map((c) => (
            <button key={String(c.v)} type="button" aria-pressed={value === c.v}
              onClick={() => onChange(value === c.v ? null : c.v)}
              className={`flex-1 py-2 rounded-lg border text-xs font-semibold font-mono transition ${
                value === c.v ? 'bg-up/15 border-up/40 text-up' : 'border-ink-600 text-ink-400 hover:text-ink-100'
              }`}
            >{c.label}</button>
          ))}
        </div>
      </div>
    )
  }
  return (
    <div>
      {label}
      <input id={id} className="input" value={value ?? ''} maxLength={2000}
        onChange={(e) => onChange(e.target.value || null)} />
    </div>
  )
}
