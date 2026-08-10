import request from './request'

export function listSettings() {
  return request.get('/settings')
}

export function updateSetting(key, value) {
  return request.put(`/settings/${key}`, { setting_value: value })
}
