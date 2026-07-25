import React, { useEffect, useState, useCallback } from 'react'
import { Navigate } from 'react-router-dom'
import ProtectedLayout from '../components/ProtectedLayout.jsx'
import { useAuth } from '../hooks/useAuth.js'
import {
  getAdminUsers, updateUserRole, updateUserActive,
  getAdminDatasets, getActivityLog, getSystemStats,
} from '../services/adminService.js'
import { formatNumber } from '../utils/format.js'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'users', label: 'Users' },
  { id: 'datasets', label: 'Datasets' },
  { id: 'activity', label: 'Activity Log' },
]

function formatBytes(bytes) {
  if (!bytes) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  let value = bytes
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024
    i++
  }
  return `${value.toFixed(1)} ${units[i]}`
}

export default function Admin() {
  const { user } = useAuth()
  const [tab, setTab] = useState('overview')
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [datasets, setDatasets] = useState([])
  const [activity, setActivity] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = useCallback(async (t) => {
    setLoading(true)
    setError('')
    try {
      if (t === 'overview') setStats(await getSystemStats())
      if (t === 'users') setUsers(await getAdminUsers())
      if (t === 'datasets') setDatasets(await getAdminDatasets())
      if (t === 'activity') setActivity(await getActivityLog(100))
    } catch (err) {
      setError('Could not load admin data.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load(tab)
  }, [tab, load])

  async function handleRoleChange(userId, role) {
    try {
      const updated = await updateUserRole(userId, role)
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update role.')
    }
  }

  async function handleToggleActive(userId, isActive) {
    try {
      const updated = await updateUserActive(userId, isActive)
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)))
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not update account status.')
    }
  }

  if (user && user.role !== 'admin') {
    return <Navigate to="/dashboard" replace />
  }

  return (
    <ProtectedLayout>
      <h1 className="text-2xl font-semibold mb-1">Admin</h1>
      <p className="text-sm text-slate-500 mb-6">User management, dataset oversight, and system activity.</p>

      <div className="flex gap-1 border-b border-teal-100 mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id ? 'border-gold-500 text-ink' : 'border-transparent text-slate-500 hover:text-ink'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {error && <p className="text-sm text-negative mb-4">{error}</p>}
      {loading && <p className="text-sm text-slate-500 mb-4">Loading…</p>}

      {tab === 'overview' && stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card p-5">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Users</p>
            <p className="data-figure text-2xl font-semibold text-ink mt-2">{formatNumber(stats.total_users)}</p>
            <p className="text-xs text-slate-500 mt-1">{stats.active_users} active</p>
          </div>
          <div className="card p-5">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Datasets</p>
            <p className="data-figure text-2xl font-semibold text-ink mt-2">{formatNumber(stats.total_datasets)}</p>
            <p className="text-xs text-slate-500 mt-1">{formatNumber(stats.total_rows_ingested)} rows ingested</p>
          </div>
          <div className="card p-5">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Storage Used</p>
            <p className="data-figure text-2xl font-semibold text-ink mt-2">{formatBytes(stats.storage_bytes)}</p>
          </div>
          <div className="card p-5">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Last 7 Days</p>
            <p className="data-figure text-2xl font-semibold text-ink mt-2">{stats.signups_last_7_days}</p>
            <p className="text-xs text-slate-500 mt-1">new signups · {stats.uploads_last_7_days} uploads</p>
          </div>
        </div>
      )}

      {tab === 'users' && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-teal-100 bg-teal-50/50">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Email</th>
                <th className="px-4 py-3 font-medium">Role</th>
                <th className="px-4 py-3 font-medium">Datasets</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-teal-50">
                  <td className="px-4 py-3">{u.full_name}</td>
                  <td className="px-4 py-3 text-slate-500">{u.email}</td>
                  <td className="px-4 py-3">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      className="text-xs border border-teal-100 rounded-md px-2 py-1"
                    >
                      <option value="viewer">viewer</option>
                      <option value="analyst">analyst</option>
                      <option value="admin">admin</option>
                    </select>
                  </td>
                  <td className="px-4 py-3 font-mono">{u.dataset_count}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${u.is_active ? 'bg-positive/10 text-positive' : 'bg-negative/10 text-negative'}`}>
                      {u.is_active ? 'Active' : 'Deactivated'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleToggleActive(u.id, !u.is_active)}
                      className="text-xs text-teal-600 hover:underline"
                    >
                      {u.is_active ? 'Deactivate' : 'Reactivate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'datasets' && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-teal-100 bg-teal-50/50">
                <th className="px-4 py-3 font-medium">Name</th>
                <th className="px-4 py-3 font-medium">Owner</th>
                <th className="px-4 py-3 font-medium">Rows</th>
                <th className="px-4 py-3 font-medium">Columns</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.id} className="border-b border-teal-50">
                  <td className="px-4 py-3">{d.name}</td>
                  <td className="px-4 py-3 text-slate-500">{d.owner_email}</td>
                  <td className="px-4 py-3 font-mono">{d.row_count.toLocaleString()}</td>
                  <td className="px-4 py-3 font-mono">{d.column_count}</td>
                  <td className="px-4 py-3 capitalize">{d.status}</td>
                  <td className="px-4 py-3 text-slate-500">{new Date(d.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'activity' && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-slate-500 border-b border-teal-100 bg-teal-50/50">
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium">User</th>
                <th className="px-4 py-3 font-medium">Details</th>
                <th className="px-4 py-3 font-medium">When</th>
              </tr>
            </thead>
            <tbody>
              {activity.map((log) => (
                <tr key={log.id} className="border-b border-teal-50">
                  <td className="px-4 py-3 capitalize">{log.action.replace(/_/g, ' ')}</td>
                  <td className="px-4 py-3 text-slate-500">{log.user_email || '—'}</td>
                  <td className="px-4 py-3 text-xs text-slate-500 font-mono">
                    {Object.entries(log.details).map(([k, v]) => `${k}: ${v}`).join(', ') || '—'}
                  </td>
                  <td className="px-4 py-3 text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </ProtectedLayout>
  )
}
