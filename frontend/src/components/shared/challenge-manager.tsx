'use client'

import { FormEvent, useState } from 'react'
import { Plus, Target } from 'lucide-react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/empty-state'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  useChallengeCategories,
  useChallenges,
  useCreateChallenge,
  useCreateChallengeCategory,
  useCreateCriterion,
} from '@/hooks/useChallenges'

export function ChallengeManager({ eventId }: { eventId: string }) {
  const { data: challenges = [] } = useChallenges(eventId)
  const { data: categories = [] } = useChallengeCategories(eventId)
  const createCategory = useCreateChallengeCategory(eventId)
  const createChallenge = useCreateChallenge(eventId)
  const createCriterion = useCreateCriterion(eventId)
  const [categoryName, setCategoryName] = useState('')
  const [challengeTitle, setChallengeTitle] = useState('')
  const [challengeCategory, setChallengeCategory] = useState('')
  const [criterionName, setCriterionName] = useState('')
  const [criterionCategory, setCriterionCategory] = useState('')
  const [maxScore, setMaxScore] = useState('10')
  const [weight, setWeight] = useState('1')

  const errorMessage = (error: unknown) => {
    const response = error as { response?: { data?: { detail?: string } } }
    return response.response?.data?.detail || 'Unable to save changes'
  }

  const addCategory = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await createCategory.mutateAsync({ name: categoryName.trim() })
      setCategoryName('')
      toast.success('Category created')
    } catch (error) {
      toast.error(errorMessage(error))
    }
  }

  const addChallenge = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await createChallenge.mutateAsync({ title: challengeTitle.trim(), category_id: challengeCategory })
      setChallengeTitle('')
      toast.success('Challenge created')
    } catch (error) {
      toast.error(errorMessage(error))
    }
  }

  const addCriterion = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await createCriterion.mutateAsync({
        challenge_category_id: criterionCategory,
        name: criterionName.trim(),
        max_score: Number(maxScore),
        weight: Number(weight),
      })
      setCriterionName('')
      toast.success('Criterion created')
    } catch (error) {
      toast.error(errorMessage(error))
    }
  }

  return (
    <div className="space-y-8">
      <div className="grid gap-6 lg:grid-cols-3">
        <form onSubmit={addCategory} className="space-y-3 border-l-2 border-primary/30 pl-4">
          <h3 className="font-semibold">New category</h3>
          <Input
            aria-label="Category name"
            placeholder="Category name"
            value={categoryName}
            onChange={(event) => setCategoryName(event.target.value)}
            required
          />
          <Button type="submit" size="sm" disabled={createCategory.isPending}>
            <Plus className="mr-2 h-4 w-4" /> Add category
          </Button>
        </form>

        <form onSubmit={addChallenge} className="space-y-3 border-l-2 border-primary/30 pl-4">
          <h3 className="font-semibold">New challenge</h3>
          <Input
            aria-label="Challenge title"
            placeholder="Challenge title"
            value={challengeTitle}
            onChange={(event) => setChallengeTitle(event.target.value)}
            required
          />
          <Select value={challengeCategory} onValueChange={setChallengeCategory} required>
            <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button type="submit" size="sm" disabled={!challengeCategory || createChallenge.isPending}>
            <Plus className="mr-2 h-4 w-4" /> Add challenge
          </Button>
        </form>

        <form onSubmit={addCriterion} className="space-y-3 border-l-2 border-primary/30 pl-4">
          <h3 className="font-semibold">New criterion</h3>
          <Input
            aria-label="Criterion name"
            placeholder="Criterion name"
            value={criterionName}
            onChange={(event) => setCriterionName(event.target.value)}
            required
          />
          <Select value={criterionCategory} onValueChange={setCriterionCategory} required>
            <SelectTrigger><SelectValue placeholder="Select category" /></SelectTrigger>
            <SelectContent>
              {categories.map((category) => (
                <SelectItem key={category.id} value={category.id}>{category.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <div className="grid grid-cols-2 gap-2">
            <Input aria-label="Maximum score" type="number" min="0.1" step="0.1" value={maxScore} onChange={(event) => setMaxScore(event.target.value)} required />
            <Input aria-label="Criterion weight" type="number" min="0.1" step="0.1" value={weight} onChange={(event) => setWeight(event.target.value)} required />
          </div>
          <Button type="submit" size="sm" disabled={!criterionCategory || createCriterion.isPending}>
            <Plus className="mr-2 h-4 w-4" /> Add criterion
          </Button>
        </form>
      </div>

      {challenges.length === 0 ? (
        <EmptyState icon={<Target className="h-12 w-12" />} title="No challenges yet" description="Create a category, then add the first challenge." />
      ) : (
        <div className="divide-y border-y">
          {challenges.map((challenge) => (
            <div key={challenge.id} className="flex flex-col gap-1 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="font-medium">{challenge.title}</p>
                {challenge.description && <p className="text-sm text-muted-foreground">{challenge.description}</p>}
              </div>
              <span className="text-sm text-muted-foreground">{challenge.category?.name || 'Uncategorized'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
