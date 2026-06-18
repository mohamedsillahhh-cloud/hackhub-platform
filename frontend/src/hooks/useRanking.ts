'use client'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import type { RankingEntry } from '@/types'
import { useEffect, useState } from 'react'

export function useRanking(eventId: string) {
  return useQuery({
    queryKey: ['ranking', eventId],
    queryFn: () => apiClient.ranking.getFullRanking(eventId),
    enabled: !!eventId,
    refetchInterval: 30000,
  })
}

export function useStreamRanking(eventId: string): {
  ranking: RankingEntry[]
  isConnected: boolean
} {
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    if (!eventId) return

    const eventSource = new EventSource(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/events/${eventId}/ranking/stream`
    )

    eventSource.onopen = () => setIsConnected(true)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setRanking(data)
      } catch {
        // ignore parse errors
      }
    }

    eventSource.onerror = () => {
      setIsConnected(false)
    }

    return () => {
      eventSource.close()
    }
  }, [eventId])

  return { ranking, isConnected }
}
