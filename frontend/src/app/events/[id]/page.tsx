'use client'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import Image from 'next/image'
import { ArrowLeft, Calendar, ExternalLink, Globe, MapPin, Target, Users } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Separator } from '@/components/ui/separator'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { EmptyState } from '@/components/ui/empty-state'
import { TeamCard } from '@/components/shared/team-card'
import { RankingTable } from '@/components/shared/ranking-table'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { useEvent } from '@/hooks/useEvents'
import { useRanking } from '@/hooks/useRanking'
import { useAuth } from '@/hooks/useAuth'
import { useChallenges } from '@/hooks/useChallenges'
import { useTeams } from '@/hooks/useTeams'
import { formatDate, cn } from '@/lib/utils'

function structuredItems(value: unknown): Array<{ label: string; detail?: string }> {
  if (Array.isArray(value)) {
    return value.map((item, index) => {
      if (typeof item === 'string') return { label: item }
      if (item && typeof item === 'object') {
        const record = item as Record<string, unknown>
        const label = String(record.name || record.title || record.question || `Item ${index + 1}`)
        const detail = record.description || record.value || record.answer
        return { label, detail: detail ? String(detail) : undefined }
      }
      return { label: String(item) }
    })
  }
  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>).map(([label, detail]) => ({
      label,
      detail: typeof detail === 'string' ? detail : JSON.stringify(detail),
    }))
  }
  return []
}

export default function EventDetailPage() {
  const params = useParams()
  const id = params.id as string
  const { data: event, isLoading, error, refetch } = useEvent(id)
  const { data: ranking } = useRanking(id)
  const { data: challenges = [], isLoading: challengesLoading } = useChallenges(id)
  const { data: teams = [], isLoading: teamsLoading } = useTeams(id)
  const { isAuthenticated } = useAuth()

  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load event" onRetry={() => refetch()} className="min-h-[calc(100vh-4rem)]" />
  if (!event) return null

  const isActive = event.status === 'in_progress' || event.status === 'published'
  const prizes = structuredItems(event.prizes)
  const sponsors = structuredItems(event.sponsors)
  const faq = structuredItems(event.faq)

  return (
    <div className="min-h-screen">
      <div className="relative h-64 sm:h-80 md:h-96 overflow-hidden">
        <div className={cn(
          'absolute inset-0 bg-gradient-to-br',
          event.cover_image ? '' : 'from-blue-600/30 via-purple-600/30 to-pink-600/30'
        )}>
          {event.cover_image && (
            <Image src={event.cover_image} alt={event.title} fill unoptimized className="object-cover" />
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

                {prizes.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h2 className="text-xl font-semibold mb-3">Prizes</h2>
                      <div className="divide-y border-y">
                        {prizes.map((prize) => (
                          <div key={prize.label} className="py-3">
                            <p className="font-medium">{prize.label}</p>
                            {prize.detail && <p className="text-sm text-muted-foreground">{prize.detail}</p>}
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {sponsors.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h2 className="text-xl font-semibold mb-3">Sponsors</h2>
                      <div className="flex flex-wrap gap-x-6 gap-y-2">
                        {sponsors.map((sponsor) => (
                          <span key={sponsor.label} className="font-medium">{sponsor.label}</span>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </TabsContent>

              <TabsContent value="challenges">
                {challengesLoading ? <LoadingState /> : challenges.length === 0 ? (
                  <EmptyState icon={<Target className="h-12 w-12" />} title="No challenges published" description="The organizer has not added challenges yet." />
                ) : (
                  <div className="divide-y border-y">
                    {challenges.map((challenge) => (
                      <div key={challenge.id} className="py-5">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <p className="text-xs font-medium uppercase text-muted-foreground">{challenge.category?.name || 'Challenge'}</p>
                            <h3 className="mt-1 text-lg font-semibold">{challenge.title}</h3>
                          </div>
                          {challenge.documentation_url && (
                            <a href={challenge.documentation_url} target="_blank" rel="noreferrer" aria-label={`Open documentation for ${challenge.title}`}>
                              <Button variant="ghost" size="icon"><ExternalLink className="h-4 w-4" /></Button>
                            </a>
                          )}
                        </div>
                        {challenge.description && <p className="mt-2 text-sm text-muted-foreground">{challenge.description}</p>}
                        {challenge.requirements && <p className="mt-3 text-sm"><span className="font-medium">Requirements:</span> {challenge.requirements}</p>}
                      </div>
                    ))}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="teams">
                {teamsLoading ? <LoadingState /> : teams.length === 0 ? (
                  <EmptyState icon={<Users className="h-12 w-12" />} title="No teams registered" description="Registered teams will appear here." />
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {teams.map((team, index) => <TeamCard key={team.id} team={team} index={index} linked={false} />)}
                  </div>
                )}
              </TabsContent>

              <TabsContent value="ranking">
                <RankingTable entries={ranking || []} />
              </TabsContent>

              <TabsContent value="faq">
                {faq.length === 0 ? (
                  <EmptyState title="No questions published" description="Event FAQs will appear here." />
                ) : (
                  <Accordion type="single" collapsible className="w-full">
                    {faq.map((item, index) => (
                      <AccordionItem key={`${item.label}-${index}`} value={`item-${index}`}>
                        <AccordionTrigger>{item.label}</AccordionTrigger>
                        <AccordionContent>{item.detail}</AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                )}
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
