import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(username: string, password: string) {
    const response = await api.post('/api/v1/auth/login', {
      username,
      password
    })

    if (response.data.code === 0) {
      const { access_token, refresh_token, user: userData } = response.data.data
      
      accessToken.value = access_token
      refreshToken.value = refresh_token
      user.value = userData

      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)
      localStorage.setItem('user', JSON.stringify(userData))

      return true
    }

    return false
  }

  async function register(username: string, email: string, password: string) {
    const response = await api.post('/api/v1/auth/register', {
      username,
      email,
      password
    })

    return response.data.code === 0
  }

  function logout() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  async function fetchCurrentUser() {
    try {
      const response = await api.get('/api/v1/auth/me')
      if (response.data.code === 0) {
        user.value = response.data.data
        localStorage.setItem('user', JSON.stringify(response.data.data))
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})

