import React, { useMemo } from 'react'
import { EmptyState } from './TrendChart.jsx'

// Teal-to-gold scale so it matches the app's palette instead of a generic red/green heatmap.
function colorForValue(value, max) {
  if (max <= 0) return '#EAF3F3'
  const ratio = Math.min(value / max, 1)
  // interpolate between teal-50 and a deep teal, with a gold tint at the top end
  const r = Math.round(234 - ratio * (234 - 23))
  const g = Math.round(243 - ratio * (243 - 90))
  const b = Math.round(243 - ratio * (243 - 99))
  return `rgb(${r}, ${g}, ${b})`
}

export default function HeatmapChart({ data }) {
  const { rows, columns, cellMap, max } = useMemo(() => {
    if (!data || !data.rows || data.rows.length === 0) return { rows: [], columns: [], cellMap: {}, max: 0 }
    const cellMap = {}
    let max = 0
    for (const cell of data.cells) {
      cellMap[`${cell.row}__${cell.column}`] = cell.value
      if (cell.value > max) max = cell.value
    }
    return { rows: data.rows, columns: data.columns, cellMap, max }
  }, [data])

  if (rows.length === 0) {
    return <EmptyState message="Needs a date column plus a region/product and revenue column to build a heatmap." />
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-separate" style={{ borderSpacing: 3 }}>
        <thead>
          <tr>
            <th className="text-left text-slate-500 font-medium pr-2 pb-1"></th>
            {columns.map((c) => (
              <th key={c} className="text-slate-500 font-medium pb-1 px-1 whitespace-nowrap">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row}>
              <td className="text-slate-700 font-medium pr-2 whitespace-nowrap">{row}</td>
              {columns.map((col) => {
                const value = cellMap[`${row}__${col}`] || 0
                return (
                  <td key={col} className="p-0">
                    <div
                      title={`${row} · ${col}: $${value.toLocaleString()}`}
                      className="rounded-md h-9 min-w-[44px] flex items-center justify-center text-[10px] font-mono text-ink/70"
                      style={{ backgroundColor: colorForValue(value, max) }}
                    >
                      {value > 0 ? Math.round(value / 1000) + 'k' : ''}
                    </div>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
