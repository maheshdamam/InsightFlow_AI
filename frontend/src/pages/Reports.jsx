import React, { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import ProtectedLayout from '../components/ProtectedLayout.jsx'
import { listDatasets } from '../services/datasetService.js'
import { downloadPdfReport, downloadExcelReport, downloadPptxReport } from '../services/reportService.js'

const FORMATS = [
  { id: 'pdf', label: 'PDF Report', description: 'KPIs, top products/regions, insights, and recommendations.', fn: downloadPdfReport },
  { id: 'excel', label: 'Excel Workbook', description: 'KPI summary, trend, breakdowns, and raw data — each on its own sheet.', fn: downloadExcelReport },
  { id: 'pptx', label: 'PowerPoint Deck', description: 'Title slide, KPIs, trend chart, top products chart, and recommendations.', fn: downloadPptxReport },
]

export default function Reports() {
  const [searchParams, setSearchParams] = useSearchParams()
  const datasetId = searchParams.get('dataset')
  const [datasets, setDatasets] = useState([])
  const [downloading, setDownloading] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    listDatasets().then((all) => {
      setDatasets(all)
      if (!datasetId && all.length > 0) setSearchParams({ dataset: all[0].id })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleDownload(format) {
    if (!datasetId) return
    setError('')
    setDownloading(format.id)
    try {
      await format.fn(datasetId)
    } catch (err) {
      setError('Could not generate that report. Try again in a moment.')
    } finally {
      setDownloading(null)
    }
  }

  if (datasets.length === 0) {
    return (
      <ProtectedLayout>
        <div className="card p-10 text-center">
          <h2 className="text-lg font-semibold mb-2">No datasets to report on yet</h2>
          <p className="text-sm text-slate-500 mb-5">Upload a dataset first, then come back to export a report.</p>
          <Link to="/upload" className="btn-primary inline-block">Upload a dataset</Link>
        </div>
      </ProtectedLayout>
    )
  }

  return (
    <ProtectedLayout>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">Reports</h1>
        <select
          value={datasetId || ''}
          onChange={(e) => setSearchParams({ dataset: e.target.value })}
          className="input-field w-auto text-sm py-1.5"
        >
          {datasets.map((ds) => (
            <option key={ds.id} value={ds.id}>{ds.name}</option>
          ))}
        </select>
      </div>
      <p className="text-sm text-slate-500 mb-8">Export the current dataset's dashboard as a shareable file.</p>

      {error && <p className="text-sm text-negative mb-4">{error}</p>}

      <div className="grid md:grid-cols-3 gap-5">
        {FORMATS.map((format) => (
          <div key={format.id} className="card p-5 flex flex-col">
            <h3 className="text-sm font-semibold text-ink mb-1.5">{format.label}</h3>
            <p className="text-xs text-slate-500 flex-1 mb-4">{format.description}</p>
            <button
              onClick={() => handleDownload(format)}
              disabled={downloading === format.id}
              className="btn-primary text-sm disabled:opacity-60"
            >
              {downloading === format.id ? 'Generating…' : 'Download'}
            </button>
          </div>
        ))}
      </div>
    </ProtectedLayout>
  )
}
