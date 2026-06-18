import { create } from 'zustand'
import type { User, AuthTokens, LoginRequest, RegisterRequest } from '@/types'
import { apiClient } from '@/lib/api'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<User>
  logout: () => void
  refreshToken: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  setUser: (user: User) => void
  loadFromStorage: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  tokens: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (data: LoginRequest) => {
    const tokens = await apiClient.auth.login(data)
    localStorage.setItem('auth_tokens', JSON.stringify(tokens))
    set({ tokens, isAuthenticated: true })
    const user = await apiClient.auth.getMe()
    set({ user })
  },

  register: async (data: RegisterRequest) => {
    const user = await apiClient.auth.register(data)
    return user
  },

  logout: () => {
    localStorage.removeItem('auth_tokens')
    set({ user: null, tokens: null, isAuthenticated: false })
  },

  refreshToken: async () => {
    try {
      const { tokens } = get()
      if (!tokens?.refresh_token) throw new Error('No refresh token')
      const newTokens = await apiClient.auth.refresh(tokens.refresh_token)
      localStorage.setItem('auth_tokens', JSON.stringify(newTokens))
      set({ tokens: newTokens })
    } catch {
      get().logout()
    }
  },

  updateProfile: async (data: Partial<User>) => {
    const user = await apiClient.auth.updateProfile(data)
    set({ user })
  },

  setUser: (user: User) => {
    set({ user, isAuthenticated: true, isLoading: false })
  },

  loadFromStorage: async () => {
    try {
      if (typeof window === 'undefined') {
        set({ isLoading: false })
        return
      }
      const tokensRaw = localStorage.getItem('auth_tokens')
      if (!tokensRaw) {
        set({ isLoading: false })
        return
      }
      const tokens: AuthTokens = JSON.parse(tokensRaw)
      set({ tokens, isAuthenticated: true })
      const user = await apiClient.auth.getMe()
      set({ user, isLoading: false })
    } catch {
      localStorage.removeItem('auth_tokens')
      set({ user: null, tokens: null, isAuthenticated: false, isLoading: false })
    }
  },
}))
