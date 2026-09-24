'use client'
import axios from 'axios'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

function retryServerErrors(failureCount: number, error: Error) {
  if (axios.isAxiosError(error) && error.response && error.response.status < 500) {
    return false
  }
  return failureCount < 2
}

export function usePublicDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'public-stats'],
    queryFn: () => apiClient.dashboard.getPublicStats(),
    retry: retryServerErrors,
  })
}

export function useDashboardStats(enabled = true) {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => apiClient.dashboard.getStats(),
    enabled,
    retry: retryServerErrors,
  })
}

export function useEventStats(eventId: string) {
  return useQuery({
    queryKey: ['dashboard', 'events', eventId, 'stats'],
    queryFn: () => apiClient.dashboard.getEventStats(eventId),
    enabled: !!eventId,
    retry: retryServerErrors,
  })
}
