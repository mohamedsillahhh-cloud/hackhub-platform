'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Loader2, XCircle } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { apiClient } from '@/lib/api'

export default function VerifyEmailPage() {
  const token = useSearchParams().get('token')
  const verification = useQuery({
    queryKey: ['verify-email', token],
    queryFn: () => apiClient.auth.verifyEmail(token as string),
    enabled: Boolean(token),
    retry: false,
  })

  const isInvalid = !token || verification.isError

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle>Email verification</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5 text-center">
          {verification.isPending && token && (
            <>
              <Loader2 className="mx-auto h-9 w-9 animate-spin text-primary" />
              <p className="text-sm text-muted-foreground">Verifying your email...</p>
            </>
          )}
          {verification.isSuccess && (
            <>
              <CheckCircle2 className="mx-auto h-9 w-9 text-green-600" />
              <p className="text-sm text-muted-foreground">Your email has been verified.</p>
            </>
          )}
          {isInvalid && (
            <>
              <XCircle className="mx-auto h-9 w-9 text-destructive" />
              <p className="text-sm text-muted-foreground">This verification link is invalid or expired.</p>
            </>
          )}
          {!verification.isPending && (
            <Button asChild className="w-full">
              <Link href="/auth/login">Go to sign in</Link>
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
