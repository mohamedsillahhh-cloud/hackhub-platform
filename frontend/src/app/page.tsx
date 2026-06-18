'use client'
import { useEffect, useRef } from 'react'
import Link from 'next/link'
import { motion, useInView, useAnimation } from 'framer-motion'
import {
  Calendar, Users, Trophy, Brain, ScrollText, BarChart3,
  ArrowRight, Sparkles, ChevronRight, Github, Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAuth } from '@/hooks/useAuth'
import { useDashboardStats } from '@/hooks/useDashboard'

const features = [
  {
    icon: Calendar,
    title: 'Event Management',
    description: 'Create and manage hackathons with ease. Set timelines, challenges, and judging criteria.',
    gradient: 'from-blue-500 to-cyan-500',
  },
  {
    icon: Users,
    title: 'Smart Teams',
    description: 'AI-powered team suggestions based on skills and interests. Find your perfect teammates.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: Trophy,
    title: 'Real-time Ranking',
    description: 'Live leaderboard updates during evaluations. Watch your team climb the ranks.',
    gradient: 'from-yellow-500 to-orange-500',
  },
  {
    icon: Brain,
    title: 'AI Assistant',
    description: 'Get instant feedback on your projects with AI-powered evaluation and suggestions.',
    gradient: 'from-green-500 to-emerald-500',
  },
  {
    icon:   ScrollText,
    title: 'Certificates',
    description: 'Automatically generate verifiable certificates for participants and winners.',
    gradient: 'from-red-500 to-rose-500',
  },
  {
    icon: BarChart3,
    title: 'Analytics',
    description: 'Comprehensive analytics dashboard with insights on events, participants, and projects.',
    gradient: 'from-indigo-500 to-purple-500',
  },
]

const steps = [
  {
    step: '01',
    title: 'Create or Join',
    description: 'Organizers create events with challenges. Participants browse and register for hackathons.',
    color: 'bg-blue-500',
  },
  {
    step: '02',
    title: 'Form Teams & Build',
    description: 'Create teams, invite members, and start building your project using the tech stack of your choice.',
    color: 'bg-purple-500',
  },
  {
    step: '03',
    title: 'Submit & Compete',
    description: 'Submit your project, get evaluated by judges or AI, and compete for the top spot on the leaderboard.',
    color: 'bg-pink-500',
  },
]

function AnimatedCounter({ target, suffix = '' }: { target: number; suffix?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })
  const controls = useAnimation()

  useEffect(() => {
    if (isInView) {
      controls.start({ opacity: 1, transition: { duration: 2, ease: 'easeOut' } })
    }
  }, [isInView, target, controls])

  return (
    <span ref={ref} className="text-4xl font-bold">
      {isInView ? target : 0}
      {suffix}
    </span>
  )
}

function FeatureCard({ feature, index }: { feature: typeof features[0]; index: number }) {
  const Icon = feature.icon
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ delay: index * 0.1 }}
    >
      <Card className="group h-full hover:shadow-xl transition-all duration-300">
        <CardContent className="p-6">
          <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} p-2.5 mb-4 group-hover:scale-110 transition-transform duration-300`}>
            <Icon className="w-full h-full text-white" />
          </div>
          <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
          <p className="text-sm text-muted-foreground">{feature.description}</p>
        </CardContent>
      </Card>
    </motion.div>
  )
}

export default function HomePage() {
  const { isAuthenticated } = useAuth()
  const { data: stats } = useDashboardStats()

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 via-purple-600/20 to-pink-600/20 dark:from-blue-900/30 dark:via-purple-900/30 dark:to-pink-900/30" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(120,119,198,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(0,153,255,0.1),transparent_50%)]" />
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-1/4 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border bg-background/50 backdrop-blur-sm text-sm font-medium mb-8">
                <Sparkles className="h-4 w-4 text-primary" />
                The ultimate hackathon management platform
              </div>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight mb-6"
            >
              <span className="text-gradient">
                Organize, Compete,
              </span>
              <br />
              <span>Innovate</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10"
            >
              The all-in-one platform for hackathon organizers and participants.
              Create events, form teams, build projects, and compete in real-time.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link href="/events">
                <Button size="lg" className="group text-base">
                  View Events
                  <ChevronRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
              {!isAuthenticated && (
                <Link href="/auth/register">
                  <Button size="lg" variant="outline" className="text-base">
                    Get Started
                    <Zap className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 border-y">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { label: 'Events', target: stats?.total_events || 0, suffix: '+' },
              { label: 'Participants', target: stats?.active_participants || 0, suffix: '+' },
              { label: 'Projects', target: stats?.total_projects || 0, suffix: '+' },
              { label: 'Teams', target: stats?.total_teams || 0, suffix: '+' },
            ].map((stat, i) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="text-4xl font-bold text-gradient mb-1">
                  <AnimatedCounter target={stat.target} suffix={stat.suffix} />
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Everything you need to
              {' '}<span className="text-gradient">run a hackathon</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              From event creation to final ranking, HackHub provides all the tools you need.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <FeatureCard key={feature.title} feature={feature} index={index} />
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              How it <span className="text-gradient">works</span>
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Get started in three simple steps.
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
            {steps.map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.15 }}
                className="relative"
              >
                <div className="text-center">
                  <div className={`w-16 h-16 ${step.color} rounded-2xl flex items-center justify-center mx-auto mb-6 text-white font-bold text-xl`}>
                    {step.step}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                  <p className="text-muted-foreground">{step.description}</p>
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 -right-4">
                    <ArrowRight className="h-6 w-6 text-muted-foreground/30" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative rounded-2xl bg-gradient-to-br from-primary via-purple-600 to-pink-600 p-12 text-center overflow-hidden"
          >
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.1),transparent_60%)]" />
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Ready to start your hackathon journey?
              </h2>
              <p className="text-lg text-white/80 max-w-2xl mx-auto mb-8">
                Join thousands of innovators already using HackHub to organize and compete in hackathons worldwide.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                {isAuthenticated ? (
                  <Link href="/events">
                    <Button size="lg" variant="secondary" className="text-base">
                      Browse Events
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                ) : (
                  <>
                    <Link href="/auth/register">
                      <Button size="lg" variant="secondary" className="text-base">
                        Get Started Free
                        <Zap className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                    <Link href="/events">
                      <Button size="lg" variant="outline" className="text-base border-white/20 text-white hover:bg-white/10">
                        View Events
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
