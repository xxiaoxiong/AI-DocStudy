export interface User {
  id: number
  username: string
  email: string
  role: string
  created_at: string
  last_login?: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

