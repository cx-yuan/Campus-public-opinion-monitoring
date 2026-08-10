import request from './request'

export function listOpinions(params) {
  return request.get('/opinions', { params })
}

export function getOpinion(id) {
  return request.get(`/opinions/${id}`)
}

export function createOpinion(data) {
  return request.post('/opinions', data)
}

export function updateOpinion(id, data) {
  return request.put(`/opinions/${id}`, data)
}

export function deleteOpinion(id) {
  return request.delete(`/opinions/${id}`)
}

export function analyzeOpinion(id) {
  return request.post(`/opinions/${id}/analyze`)
}

export function batchAnalyze() {
  return request.post('/opinions/batch-analyze')
}

export function assessRisk(id) {
  return request.post(`/opinions/${id}/risk`)
}

export function batchRisk() {
  return request.post('/opinions/batch-risk')
}
