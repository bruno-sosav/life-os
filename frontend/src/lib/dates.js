import {
  format,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  startOfMonth,
  endOfMonth,
  subDays,
  isSameDay,
  parseISO,
  differenceInCalendarDays
} from 'date-fns'
import { es } from 'date-fns/locale'

export const todayISO = () => format(new Date(), 'yyyy-MM-dd')

export const fmt = (date, pattern = 'd MMM') =>
  format(typeof date === 'string' ? parseISO(date) : date, pattern, { locale: es })

export const dayOfWeekMon0 = (date) => {
  const js = (typeof date === 'string' ? parseISO(date) : date).getDay()
  return js === 0 ? 6 : js - 1
}

export const weekRange = (date = new Date()) => {
  const start = startOfWeek(date, { weekStartsOn: 1 })
  const end = endOfWeek(date, { weekStartsOn: 1 })
  return { start, end, days: eachDayOfInterval({ start, end }) }
}

export const monthRange = (date = new Date()) => {
  const start = startOfMonth(date)
  const end = endOfMonth(date)
  return { start, end, days: eachDayOfInterval({ start, end }) }
}

export const lastNDays = (n) => {
  const end = new Date()
  const start = subDays(end, n - 1)
  return eachDayOfInterval({ start, end })
}

export {
  format,
  startOfWeek,
  endOfWeek,
  eachDayOfInterval,
  startOfMonth,
  endOfMonth,
  subDays,
  isSameDay,
  parseISO,
  differenceInCalendarDays
}
