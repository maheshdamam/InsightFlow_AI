import api from './api.js'

export async function uploadDataset(file, onProgress) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/datasets/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (evt) => {
      if (onProgress && evt.total) onProgress(Math.round((evt.loaded / evt.total) * 100))
    },
  })
  return data
}

export async function listDatasets() {
  const { data } = await api.get('/datasets')
  return data
}

export async function getDataset(id) {
  const { data } = await api.get(`/datasets/${id}`)
  return data
}

export async function renameDataset(id, name) {
  const { data } = await api.patch(`/datasets/${id}`, { name })
  return data
}

export async function deleteDataset(id) {
  await api.delete(`/datasets/${id}`)
}
