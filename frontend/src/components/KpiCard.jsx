import React from 'react'

export default function KpiCard({ label, value, delta, deltaLabel }) {
  const isPositive = typeof delta === 'number' && delta >= 0
  return (
    <div className="card p-5">
      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{label}</p>
      <p className="data-figure text-2xl font-semibold text-ink mt-2">{value}</p>
      {delta !== undefined && delta !== null && (
        <p className={`text-xs font-medium mt-1.5 ${isPositive ? 'text-positive' : 'text-negative'}`}>
          {isPositive ? '↑' : '↓'} {Math.abs(delta)}% {deltaLabel || ''}
        </p>
      )}
    </div>
  )
}
