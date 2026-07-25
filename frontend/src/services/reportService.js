import api from './api.js'

async function downloadReport(datasetId, format, extension) {
  const response = await api.post(`/reports/${datasetId}/${format}`, null, { responseType: 'blob' })
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `report.${extension}`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export const downloadPdfReport = (datasetId) => downloadReport(datasetId, 'pdf', 'pdf')
export const downloadExcelReport = (datasetId) => downloadReport(datasetId, 'excel', 'xlsx')
export const downloadPptxReport = (datasetId) => downloadReport(datasetId, 'powerpoint', 'pptx')
