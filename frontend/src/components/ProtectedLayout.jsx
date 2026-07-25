import React from 'react'
import { Navigate } from 'react-router-dom'
import { isAuthenticated } from '../services/authService.js'
import Sidebar from './Sidebar.jsx'

export default function ProtectedLayout({ children }) {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return (
    <div className="flex min-h-screen bg-surface">
      <Sidebar />
      <main className="flex-1 px-8 py-8 max-w-6xl">{children}</main>
    </div>
  )
}
