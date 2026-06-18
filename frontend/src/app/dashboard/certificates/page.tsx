'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'
import { Award, Download, Eye, ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingState } from '@/components/ui/loading-state'
import { ErrorState } from '@/components/ui/error-state'
import { EmptyState } from '@/components/ui/empty-state'
import { useAuth } from '@/hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { Certificate } from '@/types'

export default function CertificatesPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const { data: certificates, isLoading, error } = useQuery({
    queryKey: ['my-certificates'],
    queryFn: () => apiClient.certificates.list(),
    enabled: isAuthenticated,
  })

  if (authLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (!isAuthenticated) return <p className="text-center py-20 text-muted-foreground">Please log in to view certificates.</p>
  if (isLoading) return <LoadingState className="min-h-[calc(100vh-4rem)]" />
  if (error) return <ErrorState message="Failed to load certificates" />

  const certs: Certificate[] = certificates || []

  return (
    <div className="min-h-screen py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="mb-8">
            <h1 className="text-3xl font-bold">My Certificates</h1>
            <p className="text-muted-foreground mt-1">View and download your certificates</p>
          </div>

          {certs.length === 0 ? (
            <EmptyState
              icon={<Award className="h-16 w-16" />}
              title="No certificates yet"
              description="Certificates will appear here after you participate in events"
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {certs.map((cert) => (
                <motion.div key={cert.id} whileHover={{ y: -4 }}>
                  <Card className="h-full">
                    <CardHeader>
                      <div className="flex items-center gap-2">
                        <Award className="h-5 w-5 text-primary" />
                        <CardTitle className="text-lg capitalize">{cert.type}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {(cert.extra_data as Record<string, string>)?.event_title || 'Event'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Issued: {formatDate(cert.issued_at)}
                      </p>
                      <div className="flex gap-2 pt-2">
                        <Button size="sm" variant="outline" asChild>
                          <a href={`/api/v1/certificates/download/${cert.id}`} target="_blank" rel="noopener">
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </a>
                        </Button>
                        <Button size="sm" variant="outline" asChild>
                          <a href={`/api/v1/certificates/verify/${cert.verification_code}`} target="_blank" rel="noopener">
                            <Eye className="h-4 w-4 mr-1" />
                            Verify
                          </a>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
