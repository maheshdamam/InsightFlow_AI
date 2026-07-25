import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register, login } from '../services/authService.js'

export default function Register() {
  const [fullName, setFullName] = useState('')
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
      await register(fullName, email, password)
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create your account.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface p-8">
      <div className="w-full max-w-sm">
        <div className="flex items-center gap-2 mb-8">
          <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
            <path d="M2 17 Q7 8 12 13 T22 6" stroke="#D9A441" strokeWidth="2.2" strokeLinecap="round" fill="none" />
            <circle cx="22" cy="6" r="2" fill="#D9A441" />
          </svg>
          <span className="font-display font-semibold text-xl text-ink">InsightFlow AI</span>
        </div>

        <h2 className="text-2xl font-semibold mb-1">Create your workspace</h2>
        <p className="text-sm text-slate-500 mb-8">Start turning spreadsheets into decisions.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Full name</label>
            <input required className="input-field" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Jane Doe" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
            <input type="email" required className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
            <input type="password" required minLength={8} className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
          </div>

          {error && <p className="text-sm text-negative">{error}</p>}

          <button type="submit" disabled={loading} className="btn-primary w-full disabled:opacity-60">
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="text-sm text-slate-500 mt-6">
          Already have an account?{' '}
          <Link to="/login" className="text-teal-500 font-medium hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
