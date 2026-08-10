import request from './request'

export function listKeywords(params) {
  return request.get('/keywords', { params })
}

export function createKeyword(data) {
  return request.post('/keywords', data)
}

export function updateKeyword(id, data) {
  return request.put(`/keywords/${id}`, data)
}

export function deleteKeyword(id) {
  return request.delete(`/keywords/${id}`)
}
