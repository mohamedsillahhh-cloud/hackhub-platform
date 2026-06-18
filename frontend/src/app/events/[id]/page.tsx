'use client'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Calendar, MapPin, Users, Clock, Globe, ArrowLeft } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { TeamCard } from '@/components/shared/team-card'
import { RankingTable } from '@/components/shared/ranking-table'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { useEvent } from '@/hooks/useEvents'
import { useRanking } from '@/hooks/useRanking'
import { useAuth } from '@/hooks/useAuth'
import { formatDate, cn, getStatusTextColor } from '@/lib/utils'

export default function EventDetailPage() {
  const params = useParams()
  const id = params.id as string
  const { data: event, isLoading, error, refetch } = useEvent(id)
  const { data: ranking } = useRanking(id)
  const { user, isAuthenticated } = useAuth()

  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load event" onRetry={() => refetch()} className="min-h-[calc(100vh-4rem)]" />
  if (!event) return null

  const isActive = event.status === 'in_progress' || event.status === 'published'

  return (
    <div className="min-h-screen">
      <div className="relative h-64 sm:h-80 md:h-96 overflow-hidden">
        <div className={cn(
          'absolute inset-0 bg-gradient-to-br',
          event.cover_image ? '' : 'from-blue-600/30 via-purple-600/30 to-pink-600/30'
        )}>
          {event.cover_image && (
            <img src={event.cover_image} alt={event.title} className="w-full h-full object-cover" />
          )}
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 sm:p-8">
          <div className="max-w-7xl mx-auto">
            <Link href="/events" className="inline-flex items-center gap-1 text-white/80 hover:text-white text-sm mb-3 transition-colors">
              <ArrowLeft className="h-4 w-4" />
              Back to Events
            </Link>
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant={event.status === 'in_progress' ? 'success' : event.status === 'published' ? 'default' : 'secondary'}>
                    {event.status}
                  </Badge>
                </div>
                <h1 className="text-3xl sm:text-4xl font-bold text-white">{event.title}</h1>
              </div>
              {isActive && isAuthenticated && (
                <Link href={`/events/${event.id}/register`}>
                  <Button size="lg" className="shrink-0">Register Now</Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Tabs defaultValue="overview" className="space-y-6">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="challenges">Challenges</TabsTrigger>
                <TabsTrigger value="teams">Teams</TabsTrigger>
                <TabsTrigger value="ranking">Ranking</TabsTrigger>
                <TabsTrigger value="faq">FAQ</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold mb-3">About this Event</h2>
                  <div className="prose prose-sm dark:prose-invert max-w-none">
                    <p className="text-muted-foreground whitespace-pre-wrap">{event.description}</p>
                  </div>
                </div>

                {event.prizes && Object.keys(event.prizes).length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h2 className="text-xl font-semibold mb-3">Prizes</h2>
                      <p className="text-muted-foreground whitespace-pre-wrap">{JSON.stringify(event.prizes, null, 2)}</p>
                    </div>
                  </>
                )}

                {event.sponsors && Object.keys(event.sponsors).length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h2 className="text-xl font-semibold mb-3">Sponsors</h2>
                      <p className="text-muted-foreground whitespace-pre-wrap">{JSON.stringify(event.sponsors, null, 2)}</p>
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent value="challenges">
                <Card>
                  <CardContent className="p-6">
                    <p className="text-muted-foreground">Challenges will be displayed here once added by the organizer.</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="teams">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <TeamCard team={{ id: '', name: 'Example Team', members: [], leader_id: '', invite_code: '', event_id: id } as any} />
                </div>
              </TabsContent>

              <TabsContent value="ranking">
                <RankingTable entries={ranking || []} />
              </TabsContent>

              <TabsContent value="faq">
                <Accordion type="single" collapsible className="w-full">
                  <AccordionItem value="item-1">
                    <AccordionTrigger>How do I register?</AccordionTrigger>
                    <AccordionContent>
                      Click the "Register Now" button and follow the instructions. You may need to create or join a team.
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="item-2">
                    <AccordionTrigger>What are the team size limits?</AccordionTrigger>
                    <AccordionContent>
                      Maximum team size is {event.max_team_size} members.
                    </AccordionContent>
                  </AccordionItem>
                  <AccordionItem value="item-3">
                    <AccordionTrigger>How is the evaluation done?</AccordionTrigger>
                    <AccordionContent>
                      Projects are evaluated based on predefined criteria by judges and optionally by our AI system.
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </TabsContent>
            </Tabs>
          </div>

          <div className="space-y-6">
            <Card>
              <CardContent className="p-6 space-y-4">
                <h3 className="font-semibold">Event Details</h3>
                <div className="flex items-start gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Date</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(event.start_date, 'MMM d, yyyy')} - {formatDate(event.end_date, 'MMM d, yyyy')}
                    </p>
                  </div>
                </div>
                {event.location && (
                  <div className="flex items-start gap-3">
                    <MapPin className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">Location</p>
                      <p className="text-sm text-muted-foreground">{event.location}</p>
                    </div>
                  </div>
                )}
                <div className="flex items-start gap-3">
                  <Globe className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Format</p>
                    <p className="text-sm text-muted-foreground">{event.is_online ? 'Online' : 'In-Person'}</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Users className="h-5 w-5 text-muted-foreground shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Max Team Size</p>
                    <p className="text-sm text-muted-foreground">{event.max_team_size} members</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {event.regulations && (
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-3">Regulations</h3>
                  <div className="text-sm text-muted-foreground whitespace-pre-wrap">{event.regulations}</div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
