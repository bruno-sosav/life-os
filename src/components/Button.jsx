export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  color = 'blue',
  className = '',
  ...rest
}) {
  const ACCENT = {
    blue:   '#0A84FF',
    green:  '#30D158',
    purple: '#BF5AF2',
    orange: '#FF9F0A',
    red:    '#FF453A'
  }

  const variants = {
    primary:   `text-white font-semibold`,
    secondary: `bg-white/[0.08] hover:bg-white/[0.12] border border-white/[0.1] text-white/90 font-semibold`,
    ghost:     `hover:bg-white/[0.07] text-white/60 hover:text-white/90`,
    danger:    `text-[#FF453A] hover:bg-[#FF453A]/10 font-semibold`
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-xs rounded-xl min-h-[32px]',
    md: 'px-4 py-2 text-sm rounded-xl min-h-[38px]',
    lg: 'px-5 py-3 text-sm rounded-[14px] min-h-[44px]'
  }

  const inlineStyle =
    variant === 'primary'
      ? { backgroundColor: ACCENT[color] || ACCENT.blue }
      : {}

  return (
    <button
      className={`inline-flex items-center justify-center gap-1.5 font-medium transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed active:scale-[0.97] ${variants[variant]} ${sizes[size]} ${className}`}
      style={inlineStyle}
      {...rest}
    >
      {children}
    </button>
  )
}
