import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date, formatStr: string = 'PPP'): string {
  return format(new Date(date), formatStr)
}

export function formatRelativeTime(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}

export function truncate(str: string, length: number = 100): string {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function generateInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'bg-gray-500',
    published: 'bg-blue-500',
    upcoming: 'bg-blue-500',
    in_progress: 'bg-green-500',
    active: 'bg-green-500',
    closed: 'bg-purple-500',
    completed: 'bg-purple-500',
    cancelled: 'bg-red-500',
    pending: 'bg-yellow-500',
    approved: 'bg-green-500',
    rejected: 'bg-red-500',
    submitted: 'bg-blue-500',
    finalized: 'bg-green-500',
  }
  return colors[status] || 'bg-gray-500'
}

export function getStatusTextColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'text-gray-500',
    published: 'text-blue-500',
    upcoming: 'text-blue-500',
    in_progress: 'text-green-500',
    active: 'text-green-500',
    closed: 'text-purple-500',
    completed: 'text-purple-500',
    cancelled: 'text-red-500',
    pending: 'text-yellow-500',
    approved: 'text-green-500',
    rejected: 'text-red-500',
    submitted: 'text-blue-500',
    finalized: 'text-green-500',
  }
  return colors[status] || 'text-gray-500'
}

export function getRoleBadgeColor(role: string): string {
  const colors: Record<string, string> = {
    admin: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    organizer: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    participant: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    leader: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    co_leader: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    member: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  }
  return colors[role] || 'bg-gray-100 text-gray-800'
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map(part => part.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}
