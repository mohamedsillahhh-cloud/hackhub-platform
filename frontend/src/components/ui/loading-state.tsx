import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface LoadingStateProps {
  message?: string
  className?: string
  size?: 'sm' | 'md' | 'lg'
}

export function LoadingState({ message = 'Loading...', className, size = 'lg' }: LoadingStateProps) {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }

  return (
    <div className={cn('flex flex-col items-center justify-center py-16 gap-4', className)}>
      <Loader2 className={cn('animate-spin text-primary', sizeClasses[size])} />
      <p className="text-muted-foreground text-sm">{message}</p>
    </div>
  )
}
