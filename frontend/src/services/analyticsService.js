import api from './api.js'

export async function getKpis(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/kpis`)
  return data
}

export async function getTrend(datasetId, freq = 'M') {
  const { data } = await api.get(`/analytics/${datasetId}/trend`, { params: { freq } })
  return data
}

export async function getBreakdown(datasetId, by, metric = 'revenue', topN = 10) {
  const { data } = await api.get(`/analytics/${datasetId}/breakdown`, {
    params: { by, metric, top_n: topN },
  })
  return data
}

export async function getInsights(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/insights`)
  return data
}

export async function getRecommendations(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/recommendations`)
  return data
}

export async function getColumnMapping(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/mapping`)
  return data
}

export async function askCopilot(datasetId, question) {
  const { data } = await api.post('/ai/copilot', { dataset_id: datasetId, question })
  return data
}

export async function getForecast(datasetId, targetColumn, dateColumn, periods = 30, model = 'prophet') {
  const { data } = await api.post('/ai/forecast', {
    dataset_id: datasetId,
    target_column: targetColumn,
    date_column: dateColumn,
    periods,
    model,
  })
  return data
}

export async function getHeatmap(datasetId, rowBy = 'region', freq = 'M') {
  const { data } = await api.get(`/analytics/${datasetId}/heatmap`, { params: { row_by: rowBy, freq } })
  return data
}

export async function getTreemap(datasetId, by = 'product', topN = 15) {
  const { data } = await api.get(`/analytics/${datasetId}/treemap`, { params: { by, top_n: topN } })
  return data
}

export async function getFunnel(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/funnel`)
  return data
}

export async function getSankey(datasetId, source = 'category', target = 'region') {
  const { data } = await api.get(`/analytics/${datasetId}/sankey`, { params: { source, target } })
  return data
}

export async function getGeo(datasetId) {
  const { data } = await api.get(`/analytics/${datasetId}/geo`)
  return data
}

export async function getSegments(datasetId) {
  const { data } = await api.get(`/ai/${datasetId}/segments`)
  return data
}

export async function getAnomalies(datasetId) {
  const { data } = await api.get(`/ai/${datasetId}/anomalies`)
  return data
}
