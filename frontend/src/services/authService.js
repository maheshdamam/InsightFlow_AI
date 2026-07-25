import api from './api.js'

export async function login(email, password) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  localStorage.setItem('insightflow_token', data.access_token)
  localStorage.setItem('insightflow_user', JSON.stringify(data.user))
  return data.user
}

export async function register(fullName, email, password) {
  const { data } = await api.post('/auth/register', {
    full_name: fullName,
    email,
    password,
  })
  return data
}

export function logout() {
  localStorage.removeItem('insightflow_token')
  localStorage.removeItem('insightflow_user')
}

export function getCurrentUser() {
  const raw = localStorage.getItem('insightflow_user')
  return raw ? JSON.parse(raw) : null
}

export function isAuthenticated() {
  return !!localStorage.getItem('insightflow_token')
}
