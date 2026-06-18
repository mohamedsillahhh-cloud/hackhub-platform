'use client'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { motion } from 'framer-motion'
import { ArrowLeft, Users, FolderKanban, Trophy, Eye, Save } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { RankingTable } from '@/components/shared/ranking-table'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { EventForm } from '@/components/forms/event-form'
import { useEvent, useUpdateEvent, useChangeEventStatus } from '@/hooks/useEvents'
import { useRanking } from '@/hooks/useRanking'
import { useAuth } from '@/hooks/useAuth'
import { useEventStats } from '@/hooks/useDashboard'
import { useProjects } from '@/hooks/useProjects'
import { ProjectCard } from '@/components/shared/project-card'
import { EmptyState } from '@/components/ui/empty-state'
import Link from 'next/link'
import toast from 'react-hot-toast'
import type { CreateEventRequest } from '@/types'

export default function ManageEventDetailPage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const id = params.id as string
  const isEditing = searchParams.get('edit') === 'true'
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { data: event, isLoading, error, refetch } = useEvent(id)
  const { data: ranking } = useRanking(id)
  const { data: stats, isLoading: statsLoading } = useEventStats(id)
  const { data: projectsData } = useProjects({ event_id: id })
  const updateEvent = useUpdateEvent(id)
  const changeStatus = useChangeEventStatus()

  if (authLoading) return <LoadingState />
  if (!isAuthenticated) {
    router.push('/auth/login')
    return null
  }
  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load event" onRetry={() => refetch()} className="min-h-[calc(100vh-4rem)]" />
  if (!event) return null

  const handleUpdateEvent = async (data: CreateEventRequest) => {
    try {
      await updateEvent.mutateAsync(data)
      toast.success('Event updated!')
      router.push(`/dashboard/events/${id}`)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to update event')
    }
  }

  const handleChangeStatus = async (status: string) => {
    try {
      await changeStatus.mutateAsync({ id, status })
      toast.success(`Event status changed to ${status}`)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to change status')
    }
  }

  const projects = projectsData?.items || []

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Link href="/dashboard/events" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="h-4 w-4" />
            Back to Events
          </Link>

          <div className="flex items-start justify-between mb-8">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge>{event.status}</Badge>
              </div>
              <h1 className="text-3xl font-bold">{event.title}</h1>
              <p className="text-muted-foreground mt-1">Event Management Dashboard</p>
            </div>
            <div className="flex items-center gap-2">
              <Link href={`/events/${event.id}`}>
                <Button variant="outline" size="sm">
                  <Eye className="mr-2 h-4 w-4" />
                  View Public
                </Button>
              </Link>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Teams', value: stats?.total_teams || 0, icon: Users },
              { label: 'Projects', value: stats?.total_projects || 0, icon: FolderKanban },
              { label: 'Submitted', value: stats?.projects_submitted || 0, icon: Trophy },
              { label: 'Evaluated', value: stats?.projects_evaluated || 0, icon: Eye },
            ].map((stat) => {
              const Icon = stat.icon
              return (
                <Card key={stat.label}>
                  <CardContent className="p-4 flex items-center gap-3">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-xl font-bold">{stat.value}</p>
                      <p className="text-xs text-muted-foreground">{stat.label}</p>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>

          <div className="flex flex-wrap gap-2 mb-8">
            {event.status === 'draft' && (
              <Button onClick={() => handleChangeStatus('upcoming')} size="sm">
                Publish Event
              </Button>
            )}
            {event.status === 'upcoming' && (
              <Button onClick={() => handleChangeStatus('active')} size="sm">
                Start Event
              </Button>
            )}
            {event.status === 'active' && (
              <Button onClick={() => handleChangeStatus('completed')} size="sm" variant="secondary">
                Complete Event
              </Button>
            )}
            {event.status !== 'cancelled' && event.status !== 'completed' && (
              <Button onClick={() => handleChangeStatus('cancelled')} size="sm" variant="destructive">
                Cancel Event
              </Button>
            )}
            <Link href={`/dashboard/events/${id}?edit=true`}>
              <Button variant="outline" size="sm">
                <Save className="mr-2 h-4 w-4" />
                Edit Event
              </Button>
            </Link>
          </div>

          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="challenges">Challenges</TabsTrigger>
              <TabsTrigger value="teams">Teams</TabsTrigger>
              <TabsTrigger value="evaluations">Evaluations</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle>Event Details</CardTitle>
                </CardHeader>
                <CardContent>
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-muted-foreground">Start Date</dt>
                      <dd className="font-medium">{event.start_date}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">End Date</dt>
                      <dd className="font-medium">{event.end_date}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Participants</dt>
                      <dd className="font-medium">{event.participant_count || 0}</dd>
                    </div>
                    <div>
                      <dt className="text-sm text-muted-foreground">Teams</dt>
                      <dd className="font-medium">{event.team_count || 0}</dd>
                    </div>
                  </dl>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Ranking</CardTitle>
                </CardHeader>
                <CardContent>
                  <RankingTable entries={ranking || []} />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="challenges" className="mt-6">
              <Card>
                <CardContent className="p-6">
                  <p className="text-muted-foreground">Challenge management coming soon.</p>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="teams" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                <EmptyState
                  title="No teams yet"
                  description="Teams will appear here once participants register"
                />
              </div>
            </TabsContent>

            <TabsContent value="evaluations" className="mt-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {projects.length > 0 ? (
                  projects.map((project, i) => (
                    <ProjectCard key={project.id} project={project} index={i} />
                  ))
                ) : (
                  <EmptyState
                    title="No projects submitted yet"
                    description="Submitted projects will appear here"
                  />
                )}
              </div>
            </TabsContent>
          </Tabs>
        </motion.div>
      </div>

      <Dialog open={isEditing} onOpenChange={(open) => {
        if (!open) router.push(`/dashboard/events/${id}`)
      }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Event</DialogTitle>
          </DialogHeader>
          <EventForm
            initialData={{
              title: event.title,
              description: event.description,
              short_description: event.short_description,
              cover_image_url: event.cover_image_url,
              start_date: event.start_date,
              end_date: event.end_date,
              registration_deadline: event.registration_deadline,
              location: event.location,
              is_remote: event.is_remote,
              max_participants: event.max_participants,
              max_team_size: event.max_team_size,
              prizes: event.prizes,
              sponsors: event.sponsors,
              rules: event.rules,
            }}
            onSubmit={handleUpdateEvent}
            isLoading={updateEvent.isPending}
          />
        </DialogContent>
      </Dialog>
    </div>
  )
}
