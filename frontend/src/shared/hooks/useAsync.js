import { useEffect, useState, useCallback, useRef } from 'react'

export function useAsync(fn, deps = []) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  // Cada pedido lleva un número: si llega la respuesta de uno viejo (ej. tocaste ‹ dos veces
  // rápido y el primero tardó más), se descarta en lugar de pisar la del último
  const latest = useRef(0)

  const run = useCallback(async () => {
    const id = ++latest.current
    setState((s) => ({ ...s, loading: true, error: null }))
    try {
      const data = await fn()
      if (id === latest.current) setState({ data, loading: false, error: null })
    } catch (error) {
      console.error(error)
      if (id === latest.current) setState({ data: null, loading: false, error })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run()
  }, [run])

  return { ...state, refetch: run, setData: (data) => setState((s) => ({ ...s, data })) }
}
