'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Edit2, Github, Linkedin, Globe, Mail, MapPin, GraduationCap, BookOpen, Award } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { LoadingState } from '@/components/ui/loading-state'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { useAuth } from '@/hooks/useAuth'
import { generateInitials, getRoleBadgeColor } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function ProfilePage() {
  const router = useRouter()
  const { user, isLoading, isAuthenticated, updateProfile, logout } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [editData, setEditData] = useState({
    full_name: '',
    bio: '',
    university: '',
    course: '',
    country: '',
    github_url: '',
    linkedin_url: '',
    portfolio_url: '',
    skills: '',
  })

  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (!isAuthenticated) {
    router.push('/auth/login')
    return null
  }
  if (!user) return null

  const openEditDialog = () => {
    setEditData({
      full_name: user.full_name || '',
      bio: user.bio || '',
      university: user.university || '',
      course: user.course || '',
      country: user.country || '',
      github_url: user.github_url || '',
      linkedin_url: user.linkedin_url || '',
      portfolio_url: user.portfolio_url || '',
      skills: (user.skills || []).join(', '),
    })
    setIsEditing(true)
  }

  const handleSaveProfile = async () => {
    try {
      await updateProfile({
        ...editData,
        skills: editData.skills.split(',').map((s) => s.trim()).filter(Boolean),
      })
      toast.success('Profile updated!')
      setIsEditing(false)
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Failed to update profile')
    }
  }

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-4xl mx-auto px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <Card className="text-center">
                <CardContent className="p-6">
                  <Avatar className="h-24 w-24 mx-auto mb-4">
                    <AvatarImage src={user.avatar_url} />
                    <AvatarFallback className="text-2xl">{generateInitials(user.full_name)}</AvatarFallback>
                  </Avatar>
                  <h2 className="text-xl font-bold">{user.full_name}</h2>
                  <p className="text-sm text-muted-foreground">@{user.username}</p>
                  <div className="mt-2">
                    <Badge className={getRoleBadgeColor(user.role)}>
                      {user.role}
                    </Badge>
                  </div>
                  {user.bio && (
                    <p className="text-sm text-muted-foreground mt-4">{user.bio}</p>
                  )}
                  <Button variant="outline" className="w-full mt-4" onClick={openEditDialog}>
                    <Edit2 className="mr-2 h-4 w-4" />
                    Edit Profile
                  </Button>
                </CardContent>
              </Card>
            </div>

            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>About</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {user.university && (
                    <div className="flex items-center gap-3">
                      <GraduationCap className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">University</p>
                        <p className="text-sm text-muted-foreground">{user.university}</p>
                      </div>
                    </div>
                  )}
                  {user.course && (
                    <div className="flex items-center gap-3">
                      <BookOpen className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Course</p>
                        <p className="text-sm text-muted-foreground">{user.course}</p>
                      </div>
                    </div>
                  )}
                  {user.country && (
                    <div className="flex items-center gap-3">
                      <MapPin className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="text-sm font-medium">Country</p>
                        <p className="text-sm text-muted-foreground">{user.country}</p>
                      </div>
                    </div>
                  )}
                  <div className="flex items-center gap-3">
                    <Mail className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">Email</p>
                      <p className="text-sm text-muted-foreground">{user.email}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {user.skills && user.skills.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Skills</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex flex-wrap gap-2">
                      {user.skills.map((skill) => (
                        <Badge key={skill} variant="secondary">{skill}</Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Card>
                <CardHeader>
                  <CardTitle>Links</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {user.github_url && (
                    <a href={user.github_url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
                      <Github className="h-5 w-5" />
                      GitHub
                    </a>
                  )}
                  {user.linkedin_url && (
                    <a href={user.linkedin_url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
                      <Linkedin className="h-5 w-5" />
                      LinkedIn
                    </a>
                  )}
                  {user.portfolio_url && (
                    <a href={user.portfolio_url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-3 text-sm text-muted-foreground hover:text-foreground transition-colors">
                      <Globe className="h-5 w-5" />
                      Portfolio
                    </a>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Stats</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-primary">0</p>
                      <p className="text-xs text-muted-foreground">Events</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-primary">0</p>
                      <p className="text-xs text-muted-foreground">Projects</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-primary">0</p>
                      <p className="text-xs text-muted-foreground">Certificates</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </motion.div>
      </div>

      <Dialog open={isEditing} onOpenChange={setIsEditing}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Profile</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <Input
              label="Full Name"
              value={editData.full_name}
              onChange={(e) => setEditData({ ...editData, full_name: e.target.value })}
            />
            <div className="space-y-1">
              <label className="text-sm font-medium">Bio</label>
              <textarea
                className="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                value={editData.bio}
                onChange={(e) => setEditData({ ...editData, bio: e.target.value })}
              />
            </div>
            <Input
              label="University"
              value={editData.university}
              onChange={(e) => setEditData({ ...editData, university: e.target.value })}
            />
            <Input
              label="Course"
              value={editData.course}
              onChange={(e) => setEditData({ ...editData, course: e.target.value })}
            />
            <Input
              label="Country"
              value={editData.country}
              onChange={(e) => setEditData({ ...editData, country: e.target.value })}
            />
            <Input
              label="Skills (comma separated)"
              value={editData.skills}
              onChange={(e) => setEditData({ ...editData, skills: e.target.value })}
              placeholder="React, TypeScript, Node.js"
            />
            <Separator />
            <Input
              label="GitHub URL"
              value={editData.github_url}
              onChange={(e) => setEditData({ ...editData, github_url: e.target.value })}
            />
            <Input
              label="LinkedIn URL"
              value={editData.linkedin_url}
              onChange={(e) => setEditData({ ...editData, linkedin_url: e.target.value })}
            />
            <Input
              label="Portfolio URL"
              value={editData.portfolio_url}
              onChange={(e) => setEditData({ ...editData, portfolio_url: e.target.value })}
            />
            <Button className="w-full" onClick={handleSaveProfile}>
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
