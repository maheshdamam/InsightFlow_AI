import React, { useEffect, useState, useCallback } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import ProtectedLayout from '../components/ProtectedLayout.jsx'
import KpiCard from '../components/KpiCard.jsx'
import TrendChart from '../charts/TrendChart.jsx'
import BreakdownChart from '../charts/BreakdownChart.jsx'
import HeatmapChart from '../charts/HeatmapChart.jsx'
import TreemapChart from '../charts/TreemapChart.jsx'
import FunnelChartView from '../charts/FunnelChartView.jsx'
import SankeyChart from '../charts/SankeyChart.jsx'
import GeoMapChart from '../charts/GeoMapChart.jsx'
import { listDatasets } from '../services/datasetService.js'
import {
  getKpis, getTrend, getBreakdown, getInsights, getRecommendations,
  getHeatmap, getTreemap, getFunnel, getSankey, getGeo,
  getSegments, getAnomalies,
} from '../services/analyticsService.js'
import { formatCurrency, formatNumber, formatPercent } from '../utils/format.js'

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'charts', label: 'More Charts' },
  { id: 'ml', label: 'ML Insights' },
]

export default function Dashboard() {
  const [searchParams, setSearchParams] = useSearchParams()
  const datasetId = searchParams.get('dataset')
  const [tab, setTab] = useState('overview')

  const [datasets, setDatasets] = useState([])
  const [kpis, setKpis] = useState(null)
  const [trend, setTrend] = useState([])
  const [breakdown, setBreakdown] = useState([])
  const [insights, setInsights] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const [chartData, setChartData] = useState(null)
  const [chartsLoading, setChartsLoading] = useState(false)
  const [mlData, setMlData] = useState(null)
  const [mlLoading, setMlLoading] = useState(false)

  useEffect(() => {
    listDatasets().then((all) => {
      setDatasets(all)
      if (!datasetId && all.length > 0) {
        setSearchParams({ dataset: all[0].id })
      }
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadAnalytics = useCallback(async (id) => {
    setLoading(true)
    try {
      const [k, t, b, i, r] = await Promise.all([
        getKpis(id),
        getTrend(id, 'M'),
        getBreakdown(id, 'product', 'revenue'),
        getInsights(id),
        getRecommendations(id),
      ])
      setKpis(k)
      setTrend(t)
      setBreakdown(b)
      setInsights(i)
      setRecommendations(r.recommendations || [])
    } finally {
      setLoading(false)
    }
  }, [])

  const loadCharts = useCallback(async (id) => {
    setChartsLoading(true)
    try {
      const [heatmap, treemap, funnel, sankey, geo] = await Promise.all([
        getHeatmap(id, 'region', 'M'),
        getTreemap(id, 'product'),
        getFunnel(id),
        getSankey(id, 'category', 'region'),
        getGeo(id),
      ])
      setChartData({ heatmap, treemap, funnel, sankey, geo })
    } finally {
      setChartsLoading(false)
    }
  }, [])

  const loadMl = useCallback(async (id) => {
    setMlLoading(true)
    try {
      const [segments, anomalies] = await Promise.all([getSegments(id), getAnomalies(id)])
      setMlData({ segments, anomalies })
    } finally {
      setMlLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!datasetId) return
    if (tab === 'overview') loadAnalytics(datasetId)
    if (tab === 'charts' && !chartData) loadCharts(datasetId)
    if (tab === 'ml' && !mlData) loadMl(datasetId)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [datasetId, tab])

  // Reset cached tab data when the dataset changes
  useEffect(() => {
    setChartData(null)
    setMlData(null)
  }, [datasetId])

  if (datasets.length === 0) {
    return (
      <ProtectedLayout>
        <div className="card p-10 text-center">
          <h2 className="text-lg font-semibold mb-2">No datasets yet</h2>
          <p className="text-sm text-slate-500 mb-5">Upload a CSV or Excel file to see your business dashboard.</p>
          <Link to="/upload" className="btn-primary inline-block">
            Upload a dataset
          </Link>
        </div>
      </ProtectedLayout>
    )
  }

  return (
    <ProtectedLayout>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">Dashboard</h1>
        <select
          value={datasetId || ''}
          onChange={(e) => setSearchParams({ dataset: e.target.value })}
          className="input-field w-auto text-sm py-1.5"
        >
          {datasets.map((ds) => (
            <option key={ds.id} value={ds.id}>
              {ds.name}
            </option>
          ))}
        </select>
      </div>
      <p className="text-sm text-slate-500 mb-5">Live KPIs and trends for the selected dataset.</p>

      <div className="flex gap-1 border-b border-teal-100 mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.id ? 'border-gold-500 text-ink' : 'border-transparent text-slate-500 hover:text-ink'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'overview' && (
        loading && !kpis ? (
          <p className="text-sm text-slate-500">Loading analytics…</p>
        ) : (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <KpiCard label="Total Revenue" value={formatCurrency(kpis?.total_revenue)} />
              <KpiCard label="Total Profit" value={formatCurrency(kpis?.total_profit)} />
              <KpiCard label="Profit Margin" value={formatPercent(kpis?.profit_margin_pct)} />
              <KpiCard label="Total Orders" value={formatNumber(kpis?.total_orders)} />
              <KpiCard label="Avg Order Value" value={formatCurrency(kpis?.average_order_value)} />
              <KpiCard label="Total Customers" value={formatNumber(kpis?.total_customers)} />
              <KpiCard label="Units Sold" value={formatNumber(kpis?.total_units_sold)} />
            </div>

            <div className="grid lg:grid-cols-2 gap-6 mb-6">
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-ink mb-4">Revenue Trend</h3>
                <TrendChart data={trend} />
              </div>
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-ink mb-4">Revenue by Product</h3>
                <BreakdownChart data={breakdown} />
              </div>
            </div>

            <div className="grid lg:grid-cols-2 gap-6">
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-ink mb-4">Business Insights</h3>
                {insights && Object.keys(insights).length > 0 ? (
                  <ul className="space-y-2.5 text-sm">
                    {Object.entries(insights).map(([key, value]) => (
                      <li key={key} className="flex justify-between gap-4">
                        <span className="text-slate-500 capitalize">{key.replace(/_/g, ' ')}</span>
                        <span className="font-medium text-ink text-right">
                          {Array.isArray(value) ? value.join(', ') || '—' : String(value)}
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-slate-500">Not enough recognizable columns to generate insights.</p>
                )}
              </div>

              <div className="card p-5">
                <h3 className="text-sm font-semibold text-ink mb-4 flex items-center gap-2">
                  AI Recommendations
                  <span className="text-[10px] font-medium bg-gold-500/15 text-gold-600 px-1.5 py-0.5 rounded">AI</span>
                </h3>
                <ul className="space-y-3 text-sm">
                  {recommendations.map((rec, i) => (
                    <li key={i} className="flex gap-2.5">
                      <span className="text-gold-500 mt-0.5">→</span>
                      <span className="text-slate-700">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </>
        )
      )}

      {tab === 'charts' && (
        chartsLoading && !chartData ? (
          <p className="text-sm text-slate-500">Loading charts…</p>
        ) : (
          <div className="grid lg:grid-cols-2 gap-6">
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4">Revenue Heatmap (Region × Month)</h3>
              <HeatmapChart data={chartData?.heatmap} />
            </div>
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4">Product Treemap</h3>
              <TreemapChart data={chartData?.treemap} />
            </div>
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4">Order Funnel</h3>
              <FunnelChartView data={chartData?.funnel} />
            </div>
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4">Category → Region Flow</h3>
              <SankeyChart data={chartData?.sankey} />
            </div>
            <div className="card p-5 lg:col-span-2">
              <h3 className="text-sm font-semibold text-ink mb-4">Revenue by Region (Map)</h3>
              <GeoMapChart data={chartData?.geo} />
            </div>
          </div>
        )
      )}

      {tab === 'ml' && (
        mlLoading && !mlData ? (
          <p className="text-sm text-slate-500">Running models…</p>
        ) : (
          <div className="space-y-6">
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4 flex items-center gap-2">
                Customer Segments (K-Means / RFM)
                <span className="text-[10px] font-medium bg-gold-500/15 text-gold-600 px-1.5 py-0.5 rounded">ML</span>
              </h3>
              {mlData?.segments?.error ? (
                <p className="text-sm text-slate-500">{mlData.segments.error}</p>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {mlData?.segments?.segments?.map((seg) => (
                    <div key={seg.segment} className="rounded-lg border border-teal-100 p-4">
                      <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{seg.segment}</p>
                      <p className="data-figure text-xl font-semibold text-ink mt-1">{seg.customer_count}</p>
                      <p className="text-xs text-slate-500 mt-1">customers</p>
                      <p className="text-xs text-slate-700 mt-2">
                        Avg spend: <span className="font-mono">${seg.avg_monetary.toLocaleString()}</span>
                      </p>
                      <p className="text-xs text-slate-700">
                        Last order: <span className="font-mono">{seg.avg_recency_days}d ago</span>
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card p-5">
              <h3 className="text-sm font-semibold text-ink mb-4 flex items-center gap-2">
                Anomaly Detection (Isolation Forest)
                <span className="text-[10px] font-medium bg-gold-500/15 text-gold-600 px-1.5 py-0.5 rounded">ML</span>
              </h3>
              {mlData?.anomalies?.error ? (
                <p className="text-sm text-slate-500">{mlData.anomalies.error}</p>
              ) : (
                <>
                  <p className="text-sm text-slate-700 mb-3">
                    Found <span className="font-semibold">{mlData?.anomalies?.anomalies_found}</span> unusual rows
                    out of <span className="font-semibold">{mlData?.anomalies?.total_rows_checked}</span> checked.
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                      <thead>
                        <tr className="text-left text-slate-500 border-b border-teal-100">
                          {mlData?.anomalies?.anomalies?.[0] &&
                            Object.keys(mlData.anomalies.anomalies[0]).map((col) => (
                              <th key={col} className="pb-2 pr-4 font-medium capitalize">{col.replace(/_/g, ' ')}</th>
                            ))}
                        </tr>
                      </thead>
                      <tbody>
                        {mlData?.anomalies?.anomalies?.slice(0, 10).map((row, i) => (
                          <tr key={i} className="border-b border-teal-50">
                            {Object.values(row).map((val, j) => (
                              <td key={j} className="py-2 pr-4 font-mono text-slate-700">{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          </div>
        )
      )}
    </ProtectedLayout>
  )
}
