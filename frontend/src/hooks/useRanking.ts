'use client'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { useEffect, useRef, useState } from 'react'
import type { RankingEntry } from '@/types'

export function useRanking(eventId: string) {
  return useQuery({
    queryKey: ['ranking', eventId],
    queryFn: () => apiClient.ranking.getFullRanking(eventId),
    enabled: !!eventId,
    refetchInterval: 30000,
  })
}

export function useStreamRanking(eventId: string) {
  const [ranking, setRanking] = useState<RankingEntry[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!eventId) return

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
    const token = localStorage.getItem('auth_tokens')
    let parsedToken = ''
    if (token) {
      try {
        parsedToken = JSON.parse(token).access_token
      } catch { /* empty */ }
    }

    const url = `${apiUrl}/events/${eventId}/ranking/stream?token=${parsedToken}`
    const es = new EventSource(url)
    eventSourceRef.current = es

    es.onopen = () => setIsConnected(true)

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setRanking(data)
      } catch { /* empty */ }
    }

    es.onerror = () => {
      setIsConnected(false)
    }

    return () => {
      es.close()
      setIsConnected(false)
    }
  }, [eventId])

  return { ranking, isConnected }
}
