'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { CreateTeamRequest } from '@/types'

const teamSchema = z.object({
  name: z.string().min(3, 'Team name must be at least 3 characters'),
  description: z.string().max(500, 'Description must be less than 500 characters').optional(),
})

type TeamFormData = z.infer<typeof teamSchema>

interface TeamFormProps {
  eventId: string
  onSubmit: (data: CreateTeamRequest) => Promise<void>
  isLoading?: boolean
}

export function TeamForm({ eventId, onSubmit, isLoading }: TeamFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TeamFormData>({
    resolver: zodResolver(teamSchema),
  })

  const handleFormSubmit = async (data: TeamFormData) => {
    await onSubmit({
      ...data,
      event_id: eventId,
    })
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Input
        label="Team Name"
        placeholder="Enter team name"
        error={errors.name?.message}
        {...register('name')}
      />
      <div className="space-y-1">
        <label className="text-sm font-medium">Description (optional)</label>
        <textarea
          className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          placeholder="Describe your team..."
          {...register('description')}
        />
        {errors.description && (
          <p className="text-sm text-destructive">{errors.description.message}</p>
        )}
      </div>
      <Button type="submit" className="w-full" loading={isLoading}>
        Create Team
      </Button>
    </form>
  )
}
