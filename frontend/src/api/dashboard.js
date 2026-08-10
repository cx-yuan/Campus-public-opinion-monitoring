import request from './request'

export function getStats() {
  return request.get('/dashboard/stats')
}

export function getSentiment() {
  return request.get('/dashboard/sentiment')
}

export function getPlatform() {
  return request.get('/dashboard/platform')
}

export function getTrend() {
  return request.get('/dashboard/trend')
}

export function getRisk() {
  return request.get('/dashboard/risk')
}

export function getHotOpinions(params) {
  return request.get('/dashboard/hot', { params })
}
