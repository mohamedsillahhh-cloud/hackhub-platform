'use client'
import { Toaster } from 'react-hot-toast'
import { cn } from '@/lib/utils'

export function ToastProvider() {
  return (
    <Toaster
      position="top-right"
      toastOptions={{
        className: cn(
          '!bg-background !text-foreground !border !border-border !shadow-lg'
        ),
        duration: 4000,
        style: {
          borderRadius: '0.5rem',
          padding: '12px 16px',
        },
        success: {
          iconTheme: {
            primary: 'hsl(142.1 76.2% 36.3%)',
            secondary: 'hsl(0 0% 100%)',
          },
        },
        error: {
          iconTheme: {
            primary: 'hsl(0 84.2% 60.2%)',
            secondary: 'hsl(0 0% 100%)',
          },
        },
      }}
    />
  )
}

export { toast } from 'react-hot-toast'
