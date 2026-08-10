import request from './request'

export function listTasks(params) {
  return request.get('/tasks', { params })
}

export function createTask(data) {
  return request.post('/tasks', data)
}

export function updateTask(id, data) {
  return request.put(`/tasks/${id}`, data)
}

export function deleteTask(id) {
  return request.delete(`/tasks/${id}`)
}

export function runTask(id, sync = false) {
  return request.post(`/tasks/${id}/run`, null, { params: { sync: sync ? 1 : 0 } })
}

export function quickCrawl() {
  return request.post('/tasks/quick-crawl')
}
