'use client'
import { motion } from 'framer-motion'
import { Users, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { TeamCard } from '@/components/shared/team-card'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { EmptyState } from '@/components/ui/empty-state'
import { useTeams } from '@/hooks/useTeams'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function TeamsPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const router = useRouter()
  const { data, isLoading, error, refetch } = useTeams(
    user ? { user_id: user.id } : undefined
  )

  if (authLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (!isAuthenticated) {
    router.push('/auth/login')
    return null
  }

  const teams = data?.items || []

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold">My Teams</h1>
              <p className="text-muted-foreground mt-1">Manage your teams and invitations</p>
            </div>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="rounded-lg border bg-card p-6 space-y-3">
                  <div className="h-5 bg-muted rounded w-2/3 animate-pulse" />
                  <div className="h-3 bg-muted rounded w-1/2 animate-pulse" />
                  <div className="flex -space-x-2">
                    {Array.from({ length: 3 }).map((_, j) => (
                      <div key={j} className="h-8 w-8 rounded-full bg-muted animate-pulse" />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : error ? (
            <ErrorState message="Failed to load teams" onRetry={() => refetch()} />
          ) : teams.length === 0 ? (
            <EmptyState
              icon={<Users className="h-16 w-16" />}
              title="No teams yet"
              description="Join an event to create or join a team"
              action={{ label: 'Browse Events', onClick: () => router.push('/events') }}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {teams.map((team, index) => (
                <TeamCard key={team.id} team={team} index={index} />
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
