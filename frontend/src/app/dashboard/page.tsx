'use client'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import { Users, Calendar, FolderKanban, UserCheck, TrendingUp, Plus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { DataTable } from '@/components/ui/data-table'
import { useDashboardStats } from '@/hooks/useDashboard'
import { useAuth } from '@/hooks/useAuth'
import { formatDate } from '@/lib/utils'
import Link from 'next/link'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'

const COLORS = ['#3b82f6', '#8b5cf6', '#ef4444', '#10b981', '#f59e0b', '#ec4899']

export default function DashboardPage() {
  const router = useRouter()
  const { user, isAuthenticated, isLoading: authLoading } = useAuth()
  const { data: stats, isLoading, error, refetch } = useDashboardStats()

  if (authLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (!isAuthenticated) {
    router.push('/auth/login')
    return null
  }

  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load dashboard" onRetry={() => refetch()} className="min-h-[calc(100vh-4rem)]" />
  if (!stats) return null

  const eventsByStatusData = Object.entries(stats.events_by_status || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }))

  const techData = (stats.top_technologies || []).slice(0, 10)

  const recentEventsData = (stats.recent_events || []).slice(0, 5)

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold">Dashboard</h1>
              <p className="text-muted-foreground mt-1">Welcome back, {user?.full_name}</p>
            </div>
            <Link href="/dashboard/events">
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Event
              </Button>
            </Link>
          </div>

          {/* Stat Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Total Users', value: stats.total_users, icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
              { label: 'Total Events', value: stats.total_events, icon: Calendar, color: 'text-purple-500', bg: 'bg-purple-500/10' },
              { label: 'Active Events', value: stats.events_by_status?.in_progress || 0, icon: TrendingUp, color: 'text-green-500', bg: 'bg-green-500/10' },
              { label: 'Active Participants', value: stats.active_participants, icon: UserCheck, color: 'text-orange-500', bg: 'bg-orange-500/10' },
            ].map((stat, i) => {
              const Icon = stat.icon
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                >
                  <Card>
                    <CardContent className="p-6 flex items-center gap-4">
                      <div className={`p-3 rounded-lg ${stat.bg}`}>
                        <Icon className={`h-6 w-6 ${stat.color}`} />
                      </div>
                      <div>
                        <p className="text-2xl font-bold">{stat.value}</p>
                        <p className="text-sm text-muted-foreground">{stat.label}</p>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Events by Status</CardTitle>
              </CardHeader>
              <CardContent>
                {eventsByStatusData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={eventsByStatusData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={100}
                        dataKey="value"
                      >
                        {eventsByStatusData.map((_, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Top Technologies</CardTitle>
              </CardHeader>
              <CardContent>
                {techData.length > 0 ? (
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={techData} layout="vertical">
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis type="number" className="text-xs" />
                      <YAxis type="category" dataKey="name" className="text-xs" width={100} />
                      <Tooltip />
                      <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                    No data available
                  </div>
                )}
              </CardContent>
            </Card>


          </div>

          {/* Recent Events */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Recent Events</CardTitle>
            </CardHeader>
            <CardContent>
              <DataTable
                columns={[
                  { key: 'title', header: 'Title' },
                  { key: 'status', header: 'Status' },
                  { key: 'start_date', header: 'Start Date', render: (item: any) => formatDate(item.start_date) },
                  { key: 'status', header: 'Status', render: (item: any) => item.status },
                ]}
                data={recentEventsData}
                keyExtractor={(item: any) => item.id}
              />
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}
