import React, { useMemo, useState } from 'react'
import { ComposableMap, Geographies, Geography } from 'react-simple-maps'
import { EmptyState } from './TrendChart.jsx'

const GEO_URL = '/countries-110m.json'

function colorForValue(value, max) {
  if (max <= 0) return '#E7ECEB'
  const ratio = Math.min(value / max, 1)
  const r = Math.round(207 - ratio * (207 - 18))
  const g = Math.round(230 - ratio * (230 - 60))
  const b = Math.round(230 - ratio * (230 - 68))
  return `rgb(${r}, ${g}, ${b})`
}

export default function GeoMapChart({ data }) {

  const [hovered, setHovered] = useState(null)

  console.log("Backend Geo Data:", data)
  
  const { valueByCountry, max, matchedCount } = useMemo(() => {
    if (!data || data.length === 0) return { valueByCountry: {}, max: 0, matchedCount: 0 }
    const map = {}
    let max = 0
    for (const row of data) {
      map[row.region.trim().toLowerCase()] = row.value
      if (row.value > max) max = row.value
    }
    return { valueByCountry: map, max, matchedCount: Object.keys(map).length }
  }, [data])

  if (!data || data.length === 0) {
    return <EmptyState message="No region column detected to plot on a map." />
  }

  return (
    <div className="relative">
      <ComposableMap projectionConfig={{ scale: 118 }} width={800} height={280} style={{ width: '100%', height: 280 }}>
        <Geographies geography={GEO_URL}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const name = (geo.properties.name || '').toLowerCase()
              const value = valueByCountry[name]
              console.log(geo.properties.name, value)
              
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onMouseEnter={() => setHovered(value !== undefined ? `${geo.properties.name}: $${value.toLocaleString()}` : geo.properties.name)}
                  onMouseLeave={() => setHovered(null)}
                  style={{
                    default: { fill: value !== undefined ? colorForValue(value, max) : '#EDEFEE', stroke: '#fff', strokeWidth: 0.5, outline: 'none' },
                    hover: { fill: '#D9A441', stroke: '#fff', strokeWidth: 0.5, outline: 'none' },
                    pressed: { fill: '#B88430', outline: 'none' },
                  }}
                />
              )
            })
          }
        </Geographies>
      </ComposableMap>
      {hovered && (
        <div className="absolute top-2 left-2 bg-white shadow-sm border border-teal-100 rounded-md px-2.5 py-1 text-xs text-ink">
          {hovered}
        </div>
      )}
      {matchedCount === 0 && (
        <p className="text-xs text-slate-500 mt-2">
          None of your region values matched country names on this map — this works best when the region
          column contains country names (e.g. "United States", "Germany").
        </p>
      )}
    </div>
  )
}
