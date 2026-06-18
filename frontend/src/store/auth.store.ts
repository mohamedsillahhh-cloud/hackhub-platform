import { create } from 'zustand'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { apiClient } from '@/lib/api'

interface AuthState {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (data: LoginRequest) => Promise<void>
  register: (data: RegisterRequest) => Promise<User>
  logout: () => Promise<void>
  refreshToken: () => Promise<void>
  updateProfile: (data: Partial<User>) => Promise<void>
  setUser: (user: User) => void
  loadFromStorage: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (data: LoginRequest) => {
    await apiClient.auth.login(data)
    set({ isAuthenticated: true })
    const user = await apiClient.auth.getMe()
    set({ user })
  },

  register: async (data: RegisterRequest) => {
    const user = await apiClient.auth.register(data)
    return user
  },

  logout: async () => {
    try {
      await apiClient.auth.logout()
    } catch {
      // ignore server errors on logout
    }
    set({ user: null, isAuthenticated: false })
  },

  refreshToken: async () => {
    try {
      await apiClient.auth.refresh()
    } catch {
      set({ user: null, isAuthenticated: false })
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
      const user = await apiClient.auth.getMe()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },
}))
