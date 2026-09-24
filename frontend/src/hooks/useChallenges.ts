'use client'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { CreateChallengeRequest } from '@/types'

export function useChallenges(eventId: string) {
  return useQuery({
    queryKey: ['challenges', eventId],
    queryFn: () => apiClient.challenges.list(eventId),
    enabled: !!eventId,
  })
}

export function useChallengeCategories(eventId: string) {
  return useQuery({
    queryKey: ['challenge-categories', eventId],
    queryFn: () => apiClient.challenges.listCategories(eventId),
    enabled: !!eventId,
  })
}

export function useCreateChallenge(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateChallengeRequest) => apiClient.challenges.create(eventId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['challenges', eventId] }),
  })
}

export function useCreateChallengeCategory(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      apiClient.challenges.createCategory(eventId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['challenge-categories', eventId] }),
  })
}

export function useCreateCriterion(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: {
      challenge_category_id: string
      name: string
      max_score: number
      weight: number
    }) => apiClient.challenges.createCriterion(eventId, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['challenge-categories', eventId] }),
  })
}
