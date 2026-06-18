'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { CreateTeamRequest } from '@/types'

export function useMyTeams() {
  return useQuery({
    queryKey: ['my-teams'],
    queryFn: () => apiClient.teams.listMyTeams(),
  })
}

export function useTeams(eventId: string) {
  return useQuery({
    queryKey: ['teams', eventId],
    queryFn: () => apiClient.teams.list(eventId),
    enabled: !!eventId,
  })
}

export function useTeam(eventId: string, teamId: string) {
  return useQuery({
    queryKey: ['teams', eventId, teamId],
    queryFn: () => apiClient.teams.getById(eventId, teamId),
    enabled: !!eventId && !!teamId,
  })
}

export function useTeamById(teamId: string) {
  return useQuery({
    queryKey: ['team', teamId],
    queryFn: () => apiClient.teams.getByIdStandalone(teamId),
    enabled: !!teamId,
  })
}

export function useCreateTeam(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateTeamRequest) => apiClient.teams.create(eventId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', eventId] })
      queryClient.invalidateQueries({ queryKey: ['my-teams'] })
    },
  })
}

export function useInviteMember(eventId: string, teamId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (userId: string) => apiClient.teams.invite(eventId, teamId, userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', eventId, teamId] })
    },
  })
}

export function useJoinTeam(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (inviteCode: string) => apiClient.teams.join(eventId, inviteCode),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', eventId] })
      queryClient.invalidateQueries({ queryKey: ['my-teams'] })
    },
  })
}

export function useRemoveMember(eventId: string, teamId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (memberId: string) => apiClient.teams.removeMember(eventId, teamId, memberId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', eventId, teamId] })
    },
  })
}

export function useLeaveTeam(eventId: string, teamId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () => apiClient.teams.leave(eventId, teamId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['teams', eventId] })
      queryClient.invalidateQueries({ queryKey: ['my-teams'] })
    },
  })
}
