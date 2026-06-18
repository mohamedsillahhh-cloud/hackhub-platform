'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import type { CreateEventRequest } from '@/types'

const eventSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  short_description: z.string().optional(),
  cover_image_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
  registration_deadline: z.string().optional(),
  location: z.string().optional(),
  is_remote: z.boolean().default(false),
  max_participants: z.coerce.number().min(1).optional(),
  max_team_size: z.coerce.number().min(1).default(4),
  prizes: z.string().optional(),
  sponsors: z.string().optional(),
  rules: z.string().optional(),
})

type EventFormData = z.infer<typeof eventSchema>

interface EventFormProps {
  initialData?: Partial<CreateEventRequest>
  onSubmit: (data: CreateEventRequest) => Promise<void>
  isLoading?: boolean
}

export function EventForm({ initialData, onSubmit, isLoading }: EventFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<EventFormData>({
    resolver: zodResolver(eventSchema),
    defaultValues: {
      title: initialData?.title || '',
      description: initialData?.description || '',
      short_description: initialData?.short_description || '',
      cover_image_url: initialData?.cover_image_url || '',
      start_date: initialData?.start_date || '',
      end_date: initialData?.end_date || '',
      registration_deadline: initialData?.registration_deadline || '',
      location: initialData?.location || '',
      is_remote: initialData?.is_remote || false,
      max_participants: initialData?.max_participants,
      max_team_size: initialData?.max_team_size || 4,
      prizes: initialData?.prizes || '',
      sponsors: initialData?.sponsors || '',
      rules: initialData?.rules || '',
    },
  })

  const isRemote = watch('is_remote')

  const handleFormSubmit = async (data: EventFormData) => {
    const payload: CreateEventRequest = {
      ...data,
      cover_image_url: data.cover_image_url || undefined,
      registration_deadline: data.registration_deadline || undefined,
      location: isRemote ? undefined : data.location,
      max_participants: data.max_participants || undefined,
      prizes: data.prizes || undefined,
      sponsors: data.sponsors || undefined,
      rules: data.rules || undefined,
    }
    await onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="md:col-span-2">
          <Input
            label="Event Title"
            placeholder="Enter event title"
            error={errors.title?.message}
            {...register('title')}
          />
        </div>
        <div className="md:col-span-2">
          <div className="space-y-1">
            <label className="text-sm font-medium">Description</label>
            <textarea
              className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Describe the event..."
              {...register('description')}
            />
            {errors.description && (
              <p className="text-sm text-destructive">{errors.description.message}</p>
            )}
          </div>
        </div>
        <div className="md:col-span-2">
          <Input
            label="Short Description"
            placeholder="Brief description for cards"
            error={errors.short_description?.message}
            {...register('short_description')}
          />
        </div>
        <div className="md:col-span-2">
          <Input
            label="Cover Image URL"
            placeholder="https://example.com/image.jpg"
            error={errors.cover_image_url?.message}
            {...register('cover_image_url')}
          />
        </div>
        <Input
          label="Start Date"
          type="datetime-local"
          error={errors.start_date?.message}
          {...register('start_date')}
        />
        <Input
          label="End Date"
          type="datetime-local"
          error={errors.end_date?.message}
          {...register('end_date')}
        />
        <Input
          label="Registration Deadline"
          type="datetime-local"
          error={errors.registration_deadline?.message}
          {...register('registration_deadline')}
        />
        <div className="flex items-center gap-2 pt-6">
          <Switch
            checked={isRemote}
            onCheckedChange={(checked) => setValue('is_remote', checked)}
          />
          <label className="text-sm font-medium">Remote Event</label>
        </div>
        {!isRemote && (
          <Input
            label="Location"
            placeholder="City, Venue"
            error={errors.location?.message}
            {...register('location')}
          />
        )}
        <Input
          label="Max Participants"
          type="number"
          placeholder="Leave empty for unlimited"
          error={errors.max_participants?.message}
          {...register('max_participants')}
        />
        <Input
          label="Max Team Size"
          type="number"
          error={errors.max_team_size?.message}
          {...register('max_team_size')}
        />
        <div className="md:col-span-2">
          <div className="space-y-1">
            <label className="text-sm font-medium">Prizes</label>
            <textarea
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Describe the prizes..."
              {...register('prizes')}
            />
          </div>
        </div>
        <div className="md:col-span-2">
          <Input
            label="Sponsors"
            placeholder="List of sponsors"
            error={errors.sponsors?.message}
            {...register('sponsors')}
          />
        </div>
        <div className="md:col-span-2">
          <div className="space-y-1">
            <label className="text-sm font-medium">Rules</label>
            <textarea
              className="flex min-h-[100px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              placeholder="Event rules..."
              {...register('rules')}
            />
          </div>
        </div>
      </div>
      <Button type="submit" loading={isLoading} className="w-full">
        {initialData ? 'Update Event' : 'Create Event'}
      </Button>
    </form>
  )
}
