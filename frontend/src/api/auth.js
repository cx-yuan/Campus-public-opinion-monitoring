import request from './request'

/**
 * 获取当前登录用户信息（仅返回本人，服务端基于 token 鉴权）
 */
export function getMe() {
  return request.get('/auth/me')
}

/** 修改密码 */
export function changePassword(data) {
  return request.post('/auth/change-password', data)
}

/** 获取可注册的角色（不含管理员） */
export function getRegisterRoles() {
  return request.get('/auth/register-roles')
}
