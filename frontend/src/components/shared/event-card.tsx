'use client'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Calendar, MapPin, Users } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatDate, cn } from '@/lib/utils'
import type { Event, EventStatus } from '@/types'

const statusConfig: Record<EventStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'secondary' | 'destructive' }> = {
  draft: { label: 'Draft', variant: 'secondary' },
  upcoming: { label: 'Upcoming', variant: 'default' },
  active: { label: 'Active', variant: 'success' },
  completed: { label: 'Completed', variant: 'warning' },
  cancelled: { label: 'Cancelled', variant: 'destructive' },
}

interface EventCardProps {
  event: Event
  index?: number
}

export function EventCard({ event, index = 0 }: EventCardProps) {
  const status = statusConfig[event.status]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4 }}
    >
      <Link href={`/events/${event.id}`}>
        <Card className="overflow-hidden h-full hover:shadow-lg transition-all duration-300 group">
          <div className="relative h-48 overflow-hidden">
            <div
              className={cn(
                'absolute inset-0 bg-gradient-to-br',
                event.cover_image_url
                  ? ''
                  : 'from-blue-500/20 via-purple-500/20 to-pink-500/20'
              )}
            >
              {event.cover_image_url && (
                <img
                  src={event.cover_image_url}
                  alt={event.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
              )}
            </div>
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute top-3 right-3">
              <Badge variant={status.variant}>{status.label}</Badge>
            </div>
            <div className="absolute bottom-3 left-3 right-3">
              <h3 className="text-white font-semibold text-lg leading-tight line-clamp-2">
                {event.title}
              </h3>
            </div>
          </div>
          <CardContent className="p-4 space-y-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4 shrink-0" />
              <span className="truncate">
                {formatDate(event.start_date, 'MMM d')} - {formatDate(event.end_date, 'MMM d, yyyy')}
              </span>
            </div>
            {event.location && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4 shrink-0" />
                <span className="truncate">{event.location}</span>
              </div>
            )}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Users className="h-4 w-4 shrink-0" />
              <span>{event.participant_count || 0} participants</span>
            </div>
            {event.short_description && (
              <p className="text-sm text-muted-foreground line-clamp-2 mt-2">
                {event.short_description}
              </p>
            )}
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}
