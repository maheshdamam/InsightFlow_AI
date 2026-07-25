import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { login } from '../services/authService.js'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not sign in. Check your credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-surface">
      {/* Signature hero panel */}
      <div className="hidden lg:flex flex-col justify-between bg-ink text-white p-12 relative overflow-hidden">
        <div className="relative z-10">
          <div className="flex items-center gap-2">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M2 17 Q7 8 12 13 T22 6" stroke="#D9A441" strokeWidth="2.2" strokeLinecap="round" fill="none" />
              <circle cx="22" cy="6" r="2" fill="#D9A441" />
            </svg>
            <span className="font-display font-semibold text-xl">InsightFlow AI</span>
          </div>
        </div>

        <div className="relative z-10">
          <h1 className="font-display text-4xl font-semibold leading-tight text-white mb-4">
            Every number in your<br />business, explained.
          </h1>
          <p className="text-white/60 text-sm max-w-sm">
            Upload a spreadsheet. Get cleaned data, live KPIs, forecasts, and an AI copilot
            that answers questions about your business in plain English.
          </p>
        </div>

        <FlowLines />
        <p className="relative z-10 text-xs text-white/40">© 2026 InsightFlow AI</p>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <h2 className="text-2xl font-semibold mb-1">Welcome back</h2>
          <p className="text-sm text-slate-500 mb-8">Sign in to your InsightFlow AI workspace.</p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
              <input
                type="email"
                required
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <input
                type="password"
                required
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            {error && <p className="text-sm text-negative">{error}</p>}

            <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-60">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          <p className="text-sm text-slate-500 mt-6">
            Don't have an account?{' '}
            <Link to="/register" className="text-teal-500 font-medium hover:underline">
              Create one
            </Link>
          </p>

          <p className="text-xs text-slate-500/70 mt-8">
            Demo admin: <span className="font-mono">admin@insightflow.ai</span> / ChangeMe123!
          </p>
        </div>
      </div>
    </div>
  )
}

function FlowLines() {
  return (
    <svg className="absolute inset-0 w-full h-full opacity-[0.15]" viewBox="0 0 500 500" preserveAspectRatio="none">
      <path d="M0 350 Q125 250 250 320 T500 200" stroke="#2E8C97" strokeWidth="2" fill="none" />
      <path d="M0 420 Q125 380 250 400 T500 320" stroke="#D9A441" strokeWidth="2" fill="none" />
    </svg>
  )
}
