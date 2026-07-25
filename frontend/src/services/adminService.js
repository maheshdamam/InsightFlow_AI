import api from './api.js'

export async function getAdminUsers() {
  const { data } = await api.get('/admin/users')
  return data
}

export async function updateUserRole(userId, role) {
  const { data } = await api.patch(`/admin/users/${userId}/role`, { role })
  return data
}

export async function updateUserActive(userId, isActive) {
  const { data } = await api.patch(`/admin/users/${userId}/active`, { is_active: isActive })
  return data
}

export async function getAdminDatasets() {
  const { data } = await api.get('/admin/datasets')
  return data
}

export async function getActivityLog(limit = 100) {
  const { data } = await api.get('/admin/activity', { params: { limit } })
  return data
}

export async function getSystemStats() {
  const { data } = await api.get('/admin/stats')
  return data
}
