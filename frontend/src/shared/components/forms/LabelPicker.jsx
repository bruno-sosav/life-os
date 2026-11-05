import { colorFor } from '../../lib/constants.js'

// Etiqueta libre: elegís una de las que ya usaste o escribís una nueva
export default function LabelPicker({ id, label, value, onChange, options, placeholder }) {
  return (
    <div>
      <label className="label" htmlFor={id}>{label}</label>
      {options.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {options.map((option) => {
            const color = colorFor(option)
            const selected = value === option
            return (
              <button key={option} type="button" aria-pressed={selected} onClick={() => onChange(option)}
                className={`px-2.5 py-1.5 rounded-lg border text-xs font-semibold transition-colors ${
                  selected ? '' : 'border-ink-600 bg-ink-900 text-ink-300 hover:text-ink-100'
                }`}
                style={selected ? { background: `${color}24`, borderColor: `${color}66`, color } : {}}
              >{option}</button>
            )
          })}
        </div>
      )}
      <input id={id} className="input" value={value} maxLength={30}
        onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
    </div>
  )
}
