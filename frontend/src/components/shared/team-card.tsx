'use client'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Users, Crown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { generateInitials } from '@/lib/utils'
import type { Team } from '@/types'

interface TeamCardProps {
  team: Team
  index?: number
}

export function TeamCard({ team, index = 0 }: TeamCardProps) {
  const displayMembers = team.members?.slice(0, 4) || []
  const extraCount = (team.members?.length || 0) - 4

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4 }}
    >
      <Link href={`/teams/${team.id}`}>
        <Card className="h-full hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <div className="flex items-start justify-between">
              <CardTitle className="text-lg">{team.name}</CardTitle>
              {team.leader && (
                <Badge variant="outline" className="flex items-center gap-1">
                  <Crown className="h-3 w-3 text-yellow-500" />
                  Leader
                </Badge>
              )}
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {team.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">{team.description}</p>
            )}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>{team.members?.length || 0} members</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex -space-x-2">
                {displayMembers.map((member) => (
                  <Avatar key={member.id} className="h-8 w-8 border-2 border-background">
                    <AvatarFallback className="text-xs">
                      {generateInitials(member.user.full_name)}
                    </AvatarFallback>
                  </Avatar>
                ))}
                {extraCount > 0 && (
                  <div className="h-8 w-8 rounded-full border-2 border-background bg-muted flex items-center justify-center text-xs font-medium">
                    +{extraCount}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}
