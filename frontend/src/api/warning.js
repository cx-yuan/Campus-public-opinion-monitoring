import request from './request'

export function listWarnings(params) {
  return request.get('/warnings', { params })
}

export function handleWarning(id) {
  return request.post(`/warnings/${id}/handle`)
}

export function warningCount() {
  return request.get('/warnings/count')
}
