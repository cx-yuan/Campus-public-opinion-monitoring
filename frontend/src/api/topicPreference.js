import request from './request'

export function getMyTopics() {
  return request.get('/topic-preferences')
}

export function getCategoryOptions() {
  return request.get('/topic-preferences/options')
}

export function updateMyTopics(categories) {
  return request.put('/topic-preferences', { categories })
}
