import { api } from '../../../shared/lib/api.js'

// { access_token, expires_at }
export const login = (username, password) =>
  api('/auth/login', { method: 'POST', body: { username: username.trim(), password } })
