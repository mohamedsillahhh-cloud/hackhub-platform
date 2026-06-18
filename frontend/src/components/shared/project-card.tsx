'use client'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { FolderKanban, ExternalLink, Github } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Project } from '@/types'

interface ProjectCardProps {
  project: Project
  index?: number
}

const statusConfig: Record<string, { label: string; className: string }> = {
  draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400' },
  submitted: { label: 'Submitted', className: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' },
  finalized: { label: 'Finalized', className: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' },
}

export function ProjectCard({ project, index = 0 }: ProjectCardProps) {
  const status = statusConfig[project.status]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4 }}
    >
      <Link href={`/dashboard/events/${project.event_id}`}>
        <Card className="h-full hover:shadow-lg transition-all duration-300">
          <CardHeader>
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <FolderKanban className="h-5 w-5 text-primary shrink-0" />
                <CardTitle className="text-lg">{project.name}</CardTitle>
              </div>
              <span className={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium shrink-0', status.className)}>
                {status.label}
              </span>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground line-clamp-2">{project.description}</p>
            {project.team && (
              <p className="text-sm text-muted-foreground">
                Team: <span className="font-medium text-foreground">{project.team.name}</span>
              </p>
            )}
            {project.tech_stack && project.tech_stack.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {project.tech_stack.map((tech) => (
                  <Badge key={tech} variant="secondary" className="text-xs">
                    {tech}
                  </Badge>
                ))}
              </div>
            )}
            <div className="flex items-center gap-3 pt-2">
              {project.github_url && (
                <span className="text-muted-foreground hover:text-foreground transition-colors">
                  <Github className="h-4 w-4" />
                </span>
              )}
              {project.demo_video_url && (
                <span className="text-muted-foreground hover:text-foreground transition-colors">
                  <ExternalLink className="h-4 w-4" />
                </span>
              )}

            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  )
}
