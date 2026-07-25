import React from 'react'
import { ResponsiveContainer, FunnelChart, Funnel, LabelList, Tooltip } from 'recharts'
import { EmptyState } from './TrendChart.jsx'

const COLORS = ['#123B44', '#1F6F7A', '#2E8C97', '#D9A441']

export default function FunnelChartView({ data }) {
  if (!data || data.length === 0) {
    return <EmptyState message="No revenue column detected to build a funnel." />
  }

  const shaped = data.map((d, i) => ({
    name: d.stage,
    value: d.value,
    fill: COLORS[i % COLORS.length],
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <FunnelChart>
        <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #CFE6E6', fontSize: 13 }} />
        <Funnel dataKey="value" data={shaped} isAnimationActive>
          <LabelList position="right" dataKey="name" fill="#2A363C" stroke="none" fontSize={12} />
          <LabelList position="center" dataKey="value" fill="#fff" stroke="none" fontSize={13} fontWeight={600} />
        </Funnel>
      </FunnelChart>
    </ResponsiveContainer>
  )
}
