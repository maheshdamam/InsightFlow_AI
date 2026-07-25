import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts'
import { EmptyState } from './TrendChart.jsx'

export default function BreakdownChart({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="No matching column found for this breakdown." />
  }

  // Show Top 10 products only
  const chartData = [...data]
    .sort((a, b) => b.value - a.value)
    .slice(0, 10)
    .map(item => ({
      ...item,
      shortLabel:
        item.label.length > 20
          ? item.label.substring(0, 20) + "..."
          : item.label
    }))

  // Dynamic height based on number of products
  const chartHeight = Math.max(340, chartData.length * 38)

  return (
    <ResponsiveContainer width="100%" height={chartHeight}>
      <BarChart
        data={chartData}
        layout="vertical"
        margin={{ top: 10, right: 20, left: 30, bottom: 10 }}
      >
        <CartesianGrid
          stroke="#E5E7EB"
          horizontal={false}
        />

        <XAxis
          type="number"
          tick={{ fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />

        <YAxis
          type="category"
          dataKey="shortLabel"
          width={140}
          tick={{ fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />

        <Tooltip
          formatter={(value) => [
            Number(value).toLocaleString(),
            "Revenue"
          ]}
          labelFormatter={(label, payload) =>
            payload?.[0]?.payload?.label || label
          }
        />

        <Bar
          dataKey="value"
          fill="#175A63"
          radius={[0, 6, 6, 0]}
          barSize={20}
        />
      </BarChart>
    </ResponsiveContainer>
  )
}