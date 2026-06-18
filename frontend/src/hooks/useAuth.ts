'use client'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useAuthStore } from '@/store/auth.store'
import type { LoginRequest, RegisterRequest, User } from '@/types'

export function useAuth() {
  const { user, isLoading, isAuthenticated, logout: storeLogout, updateProfile, loadFromStorage } = useAuthStore()
  const queryClient = useQueryClient()

  const loginMutation = useMutation({
    mutationFn: async (data: LoginRequest) => {
      const store = useAuthStore.getState()
      await store.login(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth'] })
    },
  })

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterRequest) => {
      return useAuthStore.getState().register(data)
    },
  })

  const logoutMutation = useMutation({
    mutationFn: async () => {
      storeLogout()
      queryClient.clear()
    },
  })

  const updateProfileMutation = useMutation({
    mutationFn: async (data: Partial<User>) => {
      await updateProfile(data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'user'] })
    },
  })

  return {
    user,
    isLoading,
    isAuthenticated,
    login: loginMutation.mutateAsync,
    register: registerMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    updateProfile: updateProfileMutation.mutateAsync,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
    isLoggingIn: loginMutation.isPending,
    isRegistering: registerMutation.isPending,
    loadFromStorage,
  }
}
