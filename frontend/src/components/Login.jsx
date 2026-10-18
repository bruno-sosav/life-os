import { useState } from 'react'
import Button from './Button.jsx'
import { api } from '../lib/api.js'
import { useAuthStore } from '../store/authStore.js'

export default function Login() {
  const login = useAuthStore((s) => s.login)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e) {
    e.preventDefault()
    if (!username.trim() || !password) return
    setLoading(true)
    setError('')
    try {
      const { access_token, expires_at } = await api('/auth/login', {
        method: 'POST',
        body: { username: username.trim(), password },
      })
      login(access_token, expires_at)
    } catch (err) {
      setError(err.message === 'Failed to fetch' ? 'No se pudo conectar con el servidor' : err.message)
      setPassword('')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen grid place-items-center px-4">
      <form onSubmit={submit} className="w-full max-w-sm space-y-4">
        <div className="flex items-center gap-2.5 mb-6">
          <div
            className="w-10 h-10 rounded-[12px] grid place-items-center"
            style={{ background: 'linear-gradient(135deg, #BF5AF2, #0A84FF)' }}
          >
            <span className="text-white text-lg font-black">L</span>
          </div>
          <div>
            <div className="font-display font-bold">Life OS</div>
            <div className="text-xs text-white/35">Iniciá sesión para continuar</div>
          </div>
        </div>

        <div>
          <label className="label" htmlFor="username">Usuario</label>
          <input
            id="username" className="input" autoComplete="username" autoCapitalize="none"
            value={username} onChange={(e) => setUsername(e.target.value)} autoFocus
          />
        </div>
        <div>
          <label className="label" htmlFor="password">Contraseña</label>
          <input
            id="password" type="password" className="input" autoComplete="current-password"
            value={password} onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {error && <p className="text-sm text-[#FF453A]">{error}</p>}

        <Button type="submit" size="lg" className="w-full" disabled={loading}>
          {loading ? 'Entrando…' : 'Entrar'}
        </Button>
      </form>
    </div>
  )
}
