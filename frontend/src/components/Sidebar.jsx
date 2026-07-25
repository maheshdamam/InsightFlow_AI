import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const baseNavItems = [
  { to: '/dashboard', label: 'Dashboard', icon: GridIcon },
  { to: '/upload', label: 'Datasets', icon: UploadIcon },
  { to: '/copilot', label: 'AI Copilot', icon: SparkIcon },
  { to: '/reports', label: 'Reports', icon: ReportIcon },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const navItems =
    user?.role === 'admin'
      ? [...baseNavItems, { to: '/admin', label: 'Admin', icon: ShieldIcon }]
      : baseNavItems

  return (
    <aside className="w-60 shrink-0 bg-ink text-white flex flex-col min-h-screen">
      <div className="px-6 py-6 flex items-center gap-2 border-b border-white/10">
        <FlowMark />
        <span className="font-display font-semibold text-lg tracking-tight">InsightFlow</span>
      </div>

      <nav className="flex-1 px-3 py-6 space-y-1">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-gold-500 rounded-full" />}
                <Icon className="w-4 h-4" />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-5 border-t border-white/10">
        <div className="flex items-center gap-2.5 mb-3">
          <div className="w-8 h-8 rounded-full bg-gold-500 text-ink flex items-center justify-center font-display font-semibold text-sm">
            {(user?.full_name || '?').charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium truncate">{user?.full_name || 'Guest'}</p>
            <p className="text-xs text-white/50 truncate capitalize">{user?.role || ''}</p>
          </div>
        </div>
        <button
          onClick={() => {
            logout()
            navigate('/login')
          }}
          className="w-full text-left text-sm text-white/60 hover:text-white transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  )
}

function FlowMark() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
      <path
        d="M2 17 Q7 8 12 13 T22 6"
        stroke="#D9A441"
        strokeWidth="2.2"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="22" cy="6" r="2" fill="#D9A441" />
    </svg>
  )
}

function GridIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="none" {...props}>
      <rect x="2" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="2" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="2" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
      <rect x="11" y="11" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  )
}

function UploadIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="none" {...props}>
      <path d="M10 13V3M10 3L6 7M10 3l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3 13v2a2 2 0 002 2h10a2 2 0 002-2v-2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function SparkIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="none" {...props}>
      <path
        d="M10 2l1.5 5L17 9l-5.5 2L10 16l-1.5-5L3 9l5.5-2L10 2z"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  )
}

function ReportIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="none" {...props}>
      <path d="M5 2.5h7l3 3v12a1 1 0 01-1 1H5a1 1 0 01-1-1v-14a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
      <path d="M7 11v4M10 8.5V15M13 12.5V15" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

function ShieldIcon(props) {
  return (
    <svg viewBox="0 0 20 20" fill="none" {...props}>
      <path
        d="M10 2l6.5 2.5v5c0 4-2.7 7-6.5 8.5-3.8-1.5-6.5-4.5-6.5-8.5v-5L10 2z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  )
}
