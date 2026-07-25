import React from 'react'
import { ResponsiveContainer, Treemap, Tooltip } from 'recharts'
import { EmptyState } from './TrendChart.jsx'

const PALETTE = ['#123B44', '#1F6F7A', '#2E8C97', '#5FA8B0', '#D9A441', '#E4B75C', '#B88430']

function TreemapCell(props) {
  const { x, y, width, height, index, name, value } = props
  if (width < 2 || height < 2) return null
  const color = PALETTE[index % PALETTE.length]
  return (
    <g>
      <rect x={x} y={y} width={width} height={height} style={{ fill: color, stroke: '#fff', strokeWidth: 2 }} />
      {width > 60 && height > 28 && (
        <text x={x + 8} y={y + 20} fill="#fff" fontSize={12} fontWeight={500}>
          {name}
        </text>
      )}
      {width > 60 && height > 44 && (
        <text x={x + 8} y={y + 38} fill="#fff" fontSize={11} opacity={0.85} className="font-mono">
          ${Number(value).toLocaleString()}
        </text>
      )}
    </g>
  )
}

export default function TreemapChart({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="No matching column found to build a treemap." />
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <Treemap
        data={data}
        dataKey="value"
        nameKey="name"
        aspectRatio={4 / 3}
        stroke="#fff"
        content={<TreemapCell />}
      >
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #CFE6E6', fontSize: 13 }}
          formatter={(value) => [`$${Number(value).toLocaleString()}`, 'Revenue']}
        />
      </Treemap>
    </ResponsiveContainer>
  )
}
