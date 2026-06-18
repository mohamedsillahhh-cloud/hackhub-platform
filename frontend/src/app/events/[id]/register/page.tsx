'use client'
import { useParams, useRouter } from 'next/navigation'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { TeamForm } from '@/components/forms/team-form'
import { useEvent } from '@/hooks/useEvents'
import { useAuth } from '@/hooks/useAuth'
import { useCreateTeam, useJoinTeam } from '@/hooks/useTeams'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { Input } from '@/components/ui/input'
import Link from 'next/link'
import toast from 'react-hot-toast'
import type { CreateTeamRequest } from '@/types'

export default function RegisterForEventPage() {
  const params = useParams()
  const router = useRouter()
  const eventId = params.id as string
  const { isAuthenticated } = useAuth()
  const { data: event, isLoading: eventLoading, error: eventError } = useEvent(eventId)
  const createTeam = useCreateTeam(eventId)
  const joinTeam = useJoinTeam(eventId)

  const [mode, setMode] = useState<'select' | 'create' | 'join'>('create')
  const [inviteCode, setInviteCode] = useState('')
  const [isJoining, setIsJoining] = useState(false)

  if (!isAuthenticated) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
        <Card className="glass-card">
          <CardContent className="p-6 text-center">
            <p className="mb-4">Please sign in to register for this event.</p>
            <Link href="/auth/login">
              <Button>Sign In</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (eventLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (eventError) return <ErrorState message="Failed to load event" className="min-h-[calc(100vh-4rem)]" />
  if (!event) return null

  const handleCreateTeam = async (data: CreateTeamRequest) => {
    try {
      await createTeam.mutateAsync(data)
      toast.success('Team created successfully!')
      router.push(`/events/${eventId}`)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create team')
    }
  }

  const handleJoinTeam = async () => {
    if (!inviteCode.trim()) return
    setIsJoining(true)
    try {
      await joinTeam.mutateAsync(inviteCode.trim())
      toast.success('Joined team successfully!')
      router.push(`/events/${eventId}`)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to join team')
    } finally {
      setIsJoining(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] py-8">
      <div className="max-w-2xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Link href={`/events/${eventId}`} className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="h-4 w-4" />
            Back to event
          </Link>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle>Register for {event.title}</CardTitle>
              <CardDescription>Create a new team or join an existing one</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-6">
                <Button
                  variant={mode === 'create' ? 'primary' : 'outline'}
                  onClick={() => setMode('create')}
                  size="sm"
                >
                  Create Team
                </Button>
                <Button
                  variant={mode === 'join' ? 'primary' : 'outline'}
                  onClick={() => setMode('join')}
                  size="sm"
                >
                  Join Team
                </Button>
              </div>

              {mode === 'create' ? (
                <TeamForm
                  eventId={eventId}
                  onSubmit={handleCreateTeam}
                  isLoading={createTeam.isPending}
                />
              ) : (
                <div className="space-y-4">
                  <Input
                    label="Invite Code"
                    placeholder="Enter team invite code"
                    value={inviteCode}
                    onChange={(e) => setInviteCode(e.target.value)}
                  />
                  <Button
                    className="w-full"
                    onClick={handleJoinTeam}
                    loading={isJoining}
                    disabled={!inviteCode.trim()}
                  >
                    Join Team
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
