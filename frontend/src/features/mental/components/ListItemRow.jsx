// Un ítem de lista: tilde, texto (tocarlo edita), "Practicar →" y ✕
export default function ListItemRow({ it, canLearn, onToggle, onRemove, onLearn, onEdit }) {
  return (
    <>
      <button onClick={() => onToggle(it)} aria-pressed={it.done} aria-label={`${it.done ? 'Desmarcar' : 'Marcar'} ${it.text}`}
        className={`ios-checkbox w-[22px] h-[22px] rounded-md border-2 grid place-items-center shrink-0 ${
          it.done ? 'bg-up border-up' : 'border-ink-500 hover:border-up'
        }`}>
        {it.done && (
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden="true">
            <path d="M2.5 6l2.5 2.5 4.5-5" stroke="#07090A" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        )}
      </button>
      <button onClick={() => onEdit(it)} className="flex-1 min-w-0 text-left" aria-label={`Editar ${it.text}`}>
        <span className={`block text-sm ${it.done ? 'line-through text-ink-400' : ''}`}>{it.text}</span>
        {it.note && <span className="block text-[11px] text-ink-400 truncate">{it.note}</span>}
      </button>
      {canLearn && (
        <button onClick={() => onLearn(it)}
          className="shrink-0 text-[11px] font-bold text-up px-2.5 py-1.5 rounded-lg border border-up/35 hover:bg-up/10">Practicar →</button>
      )}
      <button onClick={() => onRemove(it)} aria-label={`Borrar ${it.text}`}
        className="shrink-0 w-8 h-8 rounded-md grid place-items-center text-ink-500 hover:text-down hover:bg-ink-700 text-xs md:opacity-0 md:group-hover:opacity-100 md:focus:opacity-100">✕</button>
    </>
  )
}
