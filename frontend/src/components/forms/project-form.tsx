'use client'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import type { CreateProjectRequest } from '@/types'

const projectSchema = z.object({
  name: z.string().min(3, 'Project name must be at least 3 characters'),
  description: z.string().min(10, 'Description must be at least 10 characters'),
  github_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  demo_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  video_url: z.string().url('Must be a valid URL').optional().or(z.literal('')),
})

type ProjectFormData = z.infer<typeof projectSchema>

interface ProjectFormProps {
  teamId: string
  eventId: string
  challengeId?: string
  initialData?: Partial<CreateProjectRequest>
  onSubmit: (data: CreateProjectRequest) => Promise<void>
  isLoading?: boolean
}

export function ProjectForm({ teamId, eventId, challengeId, initialData, onSubmit, isLoading }: ProjectFormProps) {
  const [techStack, setTechStack] = useState<string[]>(initialData?.tech_stack || [])
  const [techInput, setTechInput] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      github_url: initialData?.github_url || '',
      demo_url: initialData?.demo_url || '',
      video_url: initialData?.video_url || '',
    },
  })

  const addTech = () => {
    const tech = techInput.trim()
    if (tech && !techStack.includes(tech)) {
      setTechStack([...techStack, tech])
      setTechInput('')
    }
  }

  const removeTech = (tech: string) => {
    setTechStack(techStack.filter((t) => t !== tech))
  }

  const handleFormSubmit = async (data: ProjectFormData) => {
    await onSubmit({
      ...data,
      github_url: data.github_url || undefined,
      demo_url: data.demo_url || undefined,
      video_url: data.video_url || undefined,
      tech_stack: techStack,
      team_id: teamId,
      event_id: eventId,
      challenge_id: challengeId,
    })
  }

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-4">
      <Input
        label="Project Name"
        placeholder="Enter project name"
        error={errors.name?.message}
        {...register('name')}
      />
      <div className="space-y-1">
        <label className="text-sm font-medium">Description</label>
        <textarea
          className="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          placeholder="Describe your project..."
          {...register('description')}
        />
        {errors.description && (
          <p className="text-sm text-destructive">{errors.description.message}</p>
        )}
      </div>
      <Input
        label="GitHub URL"
        placeholder="https://github.com/username/repo"
        error={errors.github_url?.message}
        {...register('github_url')}
      />
      <Input
        label="Demo URL"
        placeholder="https://your-demo.vercel.app"
        error={errors.demo_url?.message}
        {...register('demo_url')}
      />
      <Input
        label="Video URL"
        placeholder="https://youtube.com/watch?v=..."
        error={errors.video_url?.message}
        {...register('video_url')}
      />
      <div className="space-y-1">
        <label className="text-sm font-medium">Tech Stack</label>
        <div className="flex gap-2">
          <input
            className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            placeholder="Add a technology..."
            value={techInput}
            onChange={(e) => setTechInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                addTech()
              }
            }}
          />
          <Button type="button" variant="outline" onClick={addTech}>
            Add
          </Button>
        </div>
        {techStack.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-2">
            {techStack.map((tech) => (
              <Badge key={tech} variant="secondary" className="gap-1">
                {tech}
                <button
                  type="button"
                  onClick={() => removeTech(tech)}
                  className="hover:text-destructive transition-colors"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            ))}
          </div>
        )}
      </div>
      <Button type="submit" className="w-full" loading={isLoading}>
        {initialData ? 'Update Project' : 'Create Project'}
      </Button>
    </form>
  )
}
