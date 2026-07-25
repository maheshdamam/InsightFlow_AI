import React from 'react'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

export default function TrendChart({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="No date/revenue columns detected to plot a trend." />
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
        <CartesianGrid stroke="#EAF3F3" vertical={false} />
        <XAxis dataKey="period" tick={{ fontSize: 12, fill: '#4B5A63' }} axisLine={{ stroke: '#CFE6E6' }} tickLine={false} />
        <YAxis tick={{ fontSize: 12, fill: '#4B5A63' }} axisLine={false} tickLine={false} width={70} />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #CFE6E6', fontSize: 13 }}
          formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
        />
        <Line type="monotone" dataKey="revenue" stroke="#175A63" strokeWidth={2.5} dot={{ r: 3, fill: '#D9A441' }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export function EmptyState({ message }) {
  return (
    <div className="h-[280px] flex items-center justify-center text-sm text-slate-500 text-center px-6">
      {message}
    </div>
  )
}
