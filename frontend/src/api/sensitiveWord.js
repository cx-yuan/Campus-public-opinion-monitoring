import request from './request'

export function listSensitiveWords(params) {
  return request.get('/sensitive-words', { params })
}

export function createSensitiveWord(data) {
  return request.post('/sensitive-words', data)
}

export function updateSensitiveWord(id, data) {
  return request.put(`/sensitive-words/${id}`, data)
}

export function deleteSensitiveWord(id) {
  return request.delete(`/sensitive-words/${id}`)
}
