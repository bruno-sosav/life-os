const VARIANTS = {
  primary: 'bg-up text-ink-950 font-semibold hover:brightness-110',
  secondary: 'bg-ink-700 hover:bg-ink-600 border border-ink-600 text-ink-100 font-semibold',
  ghost: 'hover:bg-ink-700 text-ink-400 hover:text-ink-100',
  danger: 'text-down hover:bg-down/10 font-semibold'
}

const SIZES = {
  sm: 'px-3 py-1.5 text-xs rounded-lg min-h-[32px]',
  md: 'px-4 py-2 text-sm rounded-[10px] min-h-[38px]',
  lg: 'px-5 py-3 text-sm rounded-xl min-h-[44px]'
}

export default function Button({ children, variant = 'primary', size = 'md', className = '', ...rest }) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 font-medium transition-all duration-200 disabled:bg-ink-700 disabled:text-ink-500 disabled:cursor-not-allowed active:scale-[0.97] focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      {...rest}
    >
      {children}
    </button>
  )
}
