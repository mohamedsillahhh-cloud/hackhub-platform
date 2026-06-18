'use client'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export function useDashboardStats() {
  return useQuery({
    queryKey: ['dashboard', 'stats'],
    queryFn: () => apiClient.dashboard.getStats(),
  })
}

export function useEventStats(eventId: string) {
  return useQuery({
    queryKey: ['dashboard', 'events', eventId, 'stats'],
    queryFn: () => apiClient.dashboard.getEventStats(eventId),
    enabled: !!eventId,
  })
}
