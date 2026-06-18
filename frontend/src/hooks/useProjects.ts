'use client'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { CreateProjectRequest } from '@/types'

export function useProjects(eventId: string) {
  return useQuery({
    queryKey: ['projects', eventId],
    queryFn: () => apiClient.projects.list(eventId),
    enabled: !!eventId,
  })
}

export function useProject(eventId: string, projectId: string) {
  return useQuery({
    queryKey: ['projects', eventId, projectId],
    queryFn: () => apiClient.projects.getById(eventId, projectId),
    enabled: !!eventId && !!projectId,
  })
}

export function useCreateProject(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: CreateProjectRequest) => apiClient.projects.create(eventId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', eventId] })
    },
  })
}

export function useUpdateProject(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: Partial<CreateProjectRequest> }) =>
      apiClient.projects.update(eventId, projectId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', eventId] })
    },
  })
}

export function useSubmitProject(eventId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (projectId: string) => apiClient.projects.submit(eventId, projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects', eventId] })
    },
  })
}
