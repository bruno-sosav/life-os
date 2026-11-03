import { format, parseISO } from 'date-fns'
import { es } from 'date-fns/locale'

export const todayISO = () => format(new Date(), 'yyyy-MM-dd')

export const fmt = (date, pattern = 'd MMM') =>
  format(typeof date === 'string' ? parseISO(date) : date, pattern, { locale: es })

export { format, parseISO }
