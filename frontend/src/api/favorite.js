import request from './request'

export function listFavorites(params) {
  return request.get('/favorites', { params })
}

export function getFavoriteIds() {
  return request.get('/favorites/ids')
}

export function addFavorite(opinionId) {
  return request.post(`/favorites/${opinionId}`)
}

export function removeFavorite(opinionId) {
  return request.delete(`/favorites/${opinionId}`)
}
