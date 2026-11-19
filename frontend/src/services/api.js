import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

export function validateFolder(folderUrl) {
  return api.post('/api/drive/validate', { folder_url: folderUrl }).then(({ data }) => data)
}

export function getDriveFiles(folderUrl) {
  return api.post('/api/drive/files', { folder_url: folderUrl }).then(({ data }) => data)
}

export function createBatch(folderUrl, language, selectedFileIds) {
  return api.post('/api/batches', {
    folder_url: folderUrl,
    language,
    selected_file_ids: selectedFileIds,
  }).then(({ data }) => data)
}

export function getBatch(batchId) {
  return api.get(`/api/batches/${encodeURIComponent(batchId)}`).then(({ data }) => data)
}

export function exportBatch(batchId) {
  return api.get(`/api/batches/${encodeURIComponent(batchId)}/export`, { responseType: 'blob' })
}

export function isApiConnectionError(error) {
  return axios.isAxiosError(error) && !error.response
}

export async function getApiErrorMessage(error) {
  if (axios.isAxiosError(error)) {
    const responseData = error.response?.data
    if (responseData instanceof Blob) {
      try {
        const body = JSON.parse(await responseData.text())
        if (body.detail) return body.detail
      } catch {
        // The server may return a non-JSON response for errors.
      }
    } else if (typeof responseData?.detail === 'string') {
      return responseData.detail
    } else if (typeof responseData?.message === 'string') {
      return responseData.message
    }

    if (error.code === 'ECONNABORTED') {
      return 'The request took too long. Check your connection and try again.'
    }
    if (!error.response) {
      return 'Could not reach the API. Make sure the FastAPI server is running at the configured address.'
    }
    return `The API returned an error (${error.response.status}). Please try again.`
  }

  return error instanceof Error ? error.message : 'Something went wrong. Please try again.'
}
