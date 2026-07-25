import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Upload from './pages/Upload.jsx'
import Copilot from './pages/Copilot.jsx'
import Reports from './pages/Reports.jsx'
import Admin from './pages/Admin.jsx'
import { isAuthenticated } from './services/authService.js'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/upload" element={<Upload />} />
      <Route path="/copilot" element={<Copilot />} />
      <Route path="/reports" element={<Reports />} />
      <Route path="/admin" element={<Admin />} />
      <Route path="/" element={<Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
