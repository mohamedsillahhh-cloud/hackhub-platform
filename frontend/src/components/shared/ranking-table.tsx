'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { Trophy, Medal, Award } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { generateInitials, cn } from '@/lib/utils'
import type { RankingEntry } from '@/types'

interface RankingTableProps {
  entries: RankingEntry[]
  isLoading?: boolean
}

const positionIcons = {
  1: Trophy,
  2: Medal,
  3: Award,
}

const positionColors = {
  1: 'text-yellow-500',
  2: 'text-gray-400',
  3: 'text-amber-600',
}

export function RankingTable({ entries, isLoading }: RankingTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 p-4 rounded-lg bg-muted/50 animate-pulse">
            <div className="h-8 w-8 rounded-full bg-muted" />
            <div className="h-10 w-10 rounded-full bg-muted" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-32 bg-muted rounded" />
              <div className="h-3 w-24 bg-muted rounded" />
            </div>
            <div className="h-4 w-16 bg-muted rounded" />
          </div>
        ))}
      </div>
    )
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <Trophy className="h-12 w-12 mx-auto mb-3 opacity-50" />
        <p>No rankings available yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {entries.map((entry, index) => {
          const Icon = positionIcons[entry.position as keyof typeof positionIcons]
          const isTop3 = entry.position <= 3

          return (
            <motion.div
              key={entry.team.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.03 }}
              layout
              className={cn(
                'flex items-center gap-4 p-4 rounded-lg transition-colors',
                isTop3
                  ? 'bg-gradient-to-r from-yellow-500/10 via-yellow-500/5 to-transparent border border-yellow-500/20'
                  : 'hover:bg-muted/50'
              )}
            >
              <div className={cn(
                'flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm shrink-0',
                isTop3 ? 'bg-muted' : 'text-muted-foreground'
              )}>
                {isTop3 && Icon ? (
                  <Icon className={cn('h-5 w-5', positionColors[entry.position as keyof typeof positionColors])} />
                ) : (
                  <span>{entry.position}</span>
                )}
              </div>
              <Avatar className="h-10 w-10 shrink-0">
                <AvatarFallback>
                  {generateInitials(entry.team.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm truncate">{entry.team.name}</p>
                {entry.project && (
                  <p className="text-xs text-muted-foreground truncate">{entry.project.name}</p>
                )}
              </div>
              <div className="text-right shrink-0">
                <p className="font-bold text-lg">{entry.total_score?.toFixed(1)}</p>
                <p className="text-xs text-muted-foreground">points</p>
              </div>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
