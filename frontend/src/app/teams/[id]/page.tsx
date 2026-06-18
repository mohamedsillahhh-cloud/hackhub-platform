'use client'
import { useParams, useRouter } from 'next/navigation'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowLeft, Copy, Check, UserPlus, LogOut, Trash2, Crown, Shield } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { ProjectForm } from '@/components/forms/project-form'
import { useTeam, useLeaveTeam, useRemoveMember, useInviteMember } from '@/hooks/useTeams'
import { useAuth } from '@/hooks/useAuth'
import { useCreateProject } from '@/hooks/useProjects'
import { generateInitials, getRoleBadgeColor } from '@/lib/utils'
import Link from 'next/link'
import toast from 'react-hot-toast'
import type { TeamMemberRole, CreateProjectRequest } from '@/types'

export default function TeamDetailPage() {
  const params = useParams()
  const router = useRouter()
  const id = params.id as string
  const { user } = useAuth()
  const { data: team, isLoading, error, refetch } = useTeam(id)
  const leaveTeam = useLeaveTeam()
  const removeMember = useRemoveMember()
  const inviteMember = useInviteMember()
  const createProject = useCreateProject()

  const [inviteEmail, setInviteEmail] = useState('')
  const [copied, setCopied] = useState(false)
  const [showProjectForm, setShowProjectForm] = useState(false)

  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load team" onRetry={() => refetch()} className="min-h-[calc(100vh-4rem)]" />
  if (!team) return null

  const isLeader = team.leader_id === user?.id
  const isMember = team.members?.some((m) => m.user_id === user?.id)

  const handleCopyInviteCode = () => {
    navigator.clipboard.writeText(team.invite_code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Invite code copied!')
  }

  const handleInviteMember = async () => {
    if (!inviteEmail.trim()) return
    try {
      await inviteMember.mutateAsync({ teamId: id, emailOrUsername: inviteEmail.trim() })
      toast.success('Invitation sent!')
      setInviteEmail('')
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to invite member')
    }
  }

  const handleLeaveTeam = async () => {
    try {
      await leaveTeam.mutateAsync(id)
      toast.success('Left team successfully')
      router.push('/teams')
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to leave team')
    }
  }

  const handleRemoveMember = async (userId: string) => {
    try {
      await removeMember.mutateAsync({ teamId: id, userId })
      toast.success('Member removed')
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to remove member')
    }
  }

  const handleCreateProject = async (data: CreateProjectRequest) => {
    try {
      await createProject.mutateAsync(data)
      toast.success('Project created!')
      setShowProjectForm(false)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to create project')
    }
  }

  const roleLabels: Record<TeamMemberRole, string> = {
    leader: 'Leader',
    co_leader: 'Co-Leader',
    member: 'Member',
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <Link href="/teams" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-6">
            <ArrowLeft className="h-4 w-4" />
            Back to Teams
          </Link>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-2xl">{team.name}</CardTitle>
                      {team.description && (
                        <p className="text-muted-foreground mt-1">{team.description}</p>
                      )}
                    </div>
                    {team.event && (
                      <Badge variant="outline">
                        <Link href={`/events/${team.event_id}`}>{team.event.title}</Link>
                      </Badge>
                    )}
                  </div>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Members ({team.members?.length || 0})</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {team.members?.map((member) => (
                    <div key={member.id} className="flex items-center justify-between p-3 rounded-lg hover:bg-accent/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <Avatar>
                          <AvatarFallback>{generateInitials(member.user?.full_name || 'U')}</AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-sm font-medium">
                            {member.user?.full_name}
                            {member.user_id === team.leader_id && (
                              <Crown className="inline h-3 w-3 text-yellow-500 ml-1" />
                            )}
                          </p>
                          <p className="text-xs text-muted-foreground">@{member.user?.username}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={getRoleBadgeColor(member.role)}>
                          {roleLabels[member.role]}
                        </Badge>
                        {(isLeader || member.role === 'co_leader') && member.user_id !== user?.id && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRemoveMember(member.user_id)}
                            className="text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              {isLeader && !team.project && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Project</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {showProjectForm ? (
                      <ProjectForm
                        teamId={id}
                        eventId={team.event_id}
                        onSubmit={handleCreateProject}
                        isLoading={createProject.isPending}
                      />
                    ) : (
                      <Button onClick={() => setShowProjectForm(true)}>
                        Create Project
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>

            <div className="space-y-6">
              {(isLeader || isMember) && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Team Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {isLeader && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Invite Code</label>
                        <div className="flex gap-2">
                          <code className="flex-1 px-3 py-2 rounded-md bg-muted text-sm font-mono">
                            {team.invite_code}
                          </code>
                          <Button variant="outline" size="icon" onClick={handleCopyInviteCode}>
                            {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                          </Button>
                        </div>
                      </div>
                    )}

                    {isLeader && (
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Invite by Email or Username</label>
                        <div className="flex gap-2">
                          <Input
                            placeholder="email or username"
                            value={inviteEmail}
                            onChange={(e) => setInviteEmail(e.target.value)}
                          />
                          <Button variant="outline" onClick={handleInviteMember}>
                            <UserPlus className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    )}

                    <Separator />

                    {!isLeader && (
                      <Button variant="destructive" className="w-full" onClick={handleLeaveTeam}>
                        <LogOut className="mr-2 h-4 w-4" />
                        Leave Team
                      </Button>
                    )}

                    {isLeader && (
                      <Button variant="destructive" className="w-full" onClick={handleLeaveTeam}>
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete Team
                      </Button>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
