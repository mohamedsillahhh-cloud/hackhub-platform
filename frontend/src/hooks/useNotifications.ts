'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

export function useNotifications() {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiClient.notifications.list(),
    refetchInterval: 30000,
  })
}

export function useUnreadCount() {
  const { data } = useNotifications()
  const unread = data?.items?.filter((n) => !n.read).length || 0
  return unread
}

export function useMarkRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => apiClient.notifications.markRead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useMarkAllRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiClient.notifications.markAllRead(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
    },
  })
}

export function useRespondToTeamInvite() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({
      action,
      eventId,
      teamId,
      memberId,
    }: {
      action: 'accept' | 'reject'
      eventId: string
      teamId: string
      memberId: string
    }) => action === 'accept'
      ? apiClient.teams.accept(eventId, teamId, memberId)
      : apiClient.teams.reject(eventId, teamId, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] })
      queryClient.invalidateQueries({ queryKey: ['my-teams'] })
    },
  })
}
