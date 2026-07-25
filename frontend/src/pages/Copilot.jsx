import React, { useEffect, useState, useRef } from 'react'
import { useSearchParams } from 'react-router-dom'
import ProtectedLayout from '../components/ProtectedLayout.jsx'
import { listDatasets } from '../services/datasetService.js'
import { askCopilot } from '../services/analyticsService.js'

const SUGGESTED = [
  'Which product should I discontinue?',
  'Which region should I invest in?',
  'Find loss-making products',
  'Which customers contribute most revenue?',
]

export default function Copilot() {
  const [searchParams, setSearchParams] = useSearchParams()
  const datasetId = searchParams.get('dataset')
  const [datasets, setDatasets] = useState([])
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    listDatasets().then((all) => {
      setDatasets(all)
      if (!datasetId && all.length > 0) setSearchParams({ dataset: all[0].id })
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleAsk(q) {
    const text = q || question
    if (!text.trim() || !datasetId) return
    setMessages((m) => [...m, { role: 'user', text }])
    setQuestion('')
    setLoading(true)
    try {
      const res = await askCopilot(datasetId, text)
      setMessages((m) => [...m, { role: 'assistant', text: res.answer }])
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', text: 'Sorry, I ran into an error answering that.' }])
    } finally {
      setLoading(false)
    }
  }

  if (datasets.length === 0) {
    return (
      <ProtectedLayout>
        <div className="card p-10 text-center">
          <h2 className="text-lg font-semibold mb-2">No datasets to ask about yet</h2>
          <p className="text-sm text-slate-500">Upload a dataset first, then come back to chat with your data.</p>
        </div>
      </ProtectedLayout>
    )
  }

  return (
    <ProtectedLayout>
      <div className="flex items-center justify-between mb-1">
        <h1 className="text-2xl font-semibold">AI Business Copilot</h1>
        <select
          value={datasetId || ''}
          onChange={(e) => {
            setSearchParams({ dataset: e.target.value })
            setMessages([])
          }}
          className="input-field w-auto text-sm py-1.5"
        >
          {datasets.map((ds) => (
            <option key={ds.id} value={ds.id}>
              {ds.name}
            </option>
          ))}
        </select>
      </div>
      <p className="text-sm text-slate-500 mb-6">Ask questions about your business data in plain English.</p>

      <div className="card flex flex-col h-[65vh]">
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.length === 0 && (
            <div>
              <p className="text-sm text-slate-500 mb-3">Try asking:</p>
              <div className="flex flex-wrap gap-2">
                {SUGGESTED.map((s) => (
                  <button
                    key={s}
                    onClick={() => handleAsk(s)}
                    className="text-xs px-3 py-1.5 rounded-full border border-teal-100 text-teal-600 hover:bg-teal-50 transition-colors"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[75%] rounded-xl px-4 py-2.5 text-sm ${
                  m.role === 'user' ? 'bg-ink-light text-white' : 'bg-teal-50 text-slate-700'
                }`}
              >
                {m.text}
              </div>
            </div>
          ))}
          {loading && <p className="text-xs text-slate-500">Copilot is thinking…</p>}
          <div ref={endRef} />
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleAsk()
          }}
          className="border-t border-teal-100 p-3 flex gap-2"
        >
          <input
            className="input-field flex-1"
            placeholder="Ask about your business…"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button type="submit" className="btn-primary shrink-0" disabled={loading}>
            Ask
          </button>
        </form>
      </div>
    </ProtectedLayout>
  )
}
