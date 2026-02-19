import { request } from '@/shared/utils/request'
import type { LoginForm, RegisterForm, LoginResponse, User } from '../types'

export const authApi = {
  // 用户注册
  register(data: RegisterForm) {
    return request.post<User>('/api/v1/auth/register', data)
  },

  // 用户登录
  login(data: LoginForm) {
    // OAuth2PasswordRequestForm 需要使用 application/x-www-form-urlencoded 格式
    const params = new URLSearchParams()
    params.append('username', data.username)
    params.append('password', data.password)
    
    return request.post<LoginResponse>('/api/v1/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request.get<User>('/api/v1/auth/me')
  },

  // 登出
  logout() {
    return request.post('/api/v1/auth/logout')
  }
}

