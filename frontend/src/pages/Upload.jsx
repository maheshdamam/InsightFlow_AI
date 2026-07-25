import React, { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import ProtectedLayout from '../components/ProtectedLayout.jsx'
import { uploadDataset, listDatasets, deleteDataset, renameDataset } from '../services/datasetService.js'

export default function Upload() {
  const [datasets, setDatasets] = useState([])
  const [dragActive, setDragActive] = useState(false)
  const [progress, setProgress] = useState(null)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const refresh = useCallback(async () => {
    try {
      setDatasets(await listDatasets())
    } catch {
      // ignore for now
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  async function handleFile(file) {
    if (!file) return
    setError('')
    setProgress(0)
    try {
      await uploadDataset(file, setProgress)
      await refresh()
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Check the file format.')
    } finally {
      setProgress(null)
    }
  }

  function onDrop(e) {
    e.preventDefault()
    setDragActive(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this dataset? This cannot be undone.')) return
    await deleteDataset(id)
    await refresh()
  }

  async function handleRename(id, currentName) {
    const name = window.prompt('Rename dataset', currentName)
    if (!name || name === currentName) return
    await renameDataset(id, name)
    await refresh()
  }

  return (
    <ProtectedLayout>
      <h1 className="text-2xl font-semibold mb-1">Datasets</h1>
      <p className="text-sm text-slate-500 mb-8">Upload a CSV or Excel file — InsightFlow cleans it automatically.</p>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragActive(true)
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
        className={`card border-dashed border-2 p-10 text-center transition-colors ${
          dragActive ? 'border-teal-400 bg-teal-50' : 'border-teal-100'
        }`}
      >
        <p className="text-sm text-slate-700 font-medium mb-1">Drag & drop your file here</p>
        <p className="text-xs text-slate-500 mb-4">CSV or Excel, up to 200MB</p>
        <label className="btn-secondary inline-block cursor-pointer">
          Browse files
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            className="hidden"
            onChange={(e) => handleFile(e.target.files?.[0])}
          />
        </label>

        {progress !== null && (
          <div className="mt-5 max-w-xs mx-auto">
            <div className="h-1.5 bg-teal-100 rounded-full overflow-hidden">
              <div className="h-full bg-teal-500 transition-all" style={{ width: `${progress}%` }} />
            </div>
          </div>
        )}
        {error && <p className="text-sm text-negative mt-4">{error}</p>}
      </div>

      <div className="mt-8 space-y-3">
        {datasets.length === 0 && (
          <p className="text-sm text-slate-500">No datasets yet — upload one to get started.</p>
        )}
        {datasets.map((ds) => (
          <div key={ds.id} className="card p-4 flex items-center justify-between">
            <div className="min-w-0">
              <p className="font-medium text-ink truncate">{ds.name}</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {ds.row_count.toLocaleString()} rows · {ds.column_count} columns · v{ds.version} ·{' '}
                <span className="capitalize">{ds.status}</span>
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button onClick={() => navigate(`/dashboard?dataset=${ds.id}`)} className="btn-secondary text-sm px-3 py-1.5">
                View
              </button>
              <button onClick={() => handleRename(ds.id, ds.name)} className="text-sm text-slate-500 hover:text-ink px-2">
                Rename
              </button>
              <button onClick={() => handleDelete(ds.id)} className="text-sm text-negative hover:underline px-2">
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </ProtectedLayout>
  )
}
