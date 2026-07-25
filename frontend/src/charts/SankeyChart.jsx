import React, { useMemo } from 'react'
import { sankey, sankeyLinkHorizontal } from 'd3-sankey'
import { EmptyState } from './TrendChart.jsx'

const WIDTH = 640
const HEIGHT = 280
const NODE_COLORS = ['#123B44', '#1F6F7A', '#2E8C97', '#5FA8B0', '#D9A441', '#E4B75C', '#B88430', '#175A63']

export default function SankeyChart({ data }) {
  const layout = useMemo(() => {
    if (!data || !data.nodes || data.nodes.length === 0 || !data.links || data.links.length === 0) return null
    try {
      const generator = sankey()
        .nodeWidth(16)
        .nodePadding(12)
        .extent([[1, 1], [WIDTH - 1, HEIGHT - 6]])

      // d3-sankey mutates the input, so clone defensively
      const graph = generator({
        nodes: data.nodes.map((d) => ({ ...d })),
        links: data.links.map((d) => ({ ...d })),
      })
      return graph
    } catch {
      return null
    }
  }, [data])

  if (!layout) {
    return <EmptyState message="Needs two categorical columns (e.g. category and region) to build a flow diagram." />
  }

  return (
    <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} width="100%" height={HEIGHT}>
      <g>
        {layout.links.map((link, i) => (
          <path
            key={i}
            d={sankeyLinkHorizontal()(link)}
            fill="none"
            stroke={NODE_COLORS[link.source.index % NODE_COLORS.length]}
            strokeOpacity={0.25}
            strokeWidth={Math.max(1, link.width)}
          >
            <title>
              {link.source.name} → {link.target.name}: {Math.round(link.value).toLocaleString()}
            </title>
          </path>
        ))}
        {layout.nodes.map((node, i) => (
          <g key={i}>
            <rect
              x={node.x0}
              y={node.y0}
              width={node.x1 - node.x0}
              height={Math.max(1, node.y1 - node.y0)}
              fill={NODE_COLORS[i % NODE_COLORS.length]}
              rx={2}
            >
              <title>{node.name}</title>
            </rect>
            <text
              x={node.x0 < WIDTH / 2 ? node.x1 + 6 : node.x0 - 6}
              y={(node.y0 + node.y1) / 2}
              dy="0.35em"
              fontSize={11}
              fill="#2A363C"
              textAnchor={node.x0 < WIDTH / 2 ? 'start' : 'end'}
            >
              {node.name}
            </text>
          </g>
        ))}
      </g>
    </svg>
  )
}
