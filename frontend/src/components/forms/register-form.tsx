'use client'
import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Eye, EyeOff, Mail, Lock, User, AtSign } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/hooks/useAuth'
import toast from 'react-hot-toast'

const registerSchema = z.object({
  full_name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  username: z.string().min(3, 'Username must be at least 3 characters').regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
})

type RegisterFormData = z.infer<typeof registerSchema>

export function RegisterForm() {
  const [showPassword, setShowPassword] = useState(false)
  const router = useRouter()
  const { register: registerUser, isRegistering } = useAuth()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  })

  const onSubmit = async (data: RegisterFormData) => {
    try {
      await registerUser(data)
      toast.success('Account created successfully! Please sign in.')
      router.push('/auth/login')
    } catch (error: any) {
      toast.error(error?.response?.data?.detail || 'Registration failed. Please try again.')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Input
        label="Full Name"
        placeholder="John Doe"
        icon={<User className="h-4 w-4" />}
        error={errors.full_name?.message}
        {...register('full_name')}
      />
      <Input
        label="Email"
        type="email"
        placeholder="you@example.com"
        icon={<Mail className="h-4 w-4" />}
        error={errors.email?.message}
        {...register('email')}
      />
      <Input
        label="Username"
        placeholder="johndoe"
        icon={<AtSign className="h-4 w-4" />}
        error={errors.username?.message}
        {...register('username')}
      />
      <Input
        label="Password"
        type={showPassword ? 'text' : 'password'}
        placeholder="Create a password"
        icon={<Lock className="h-4 w-4" />}
        error={errors.password?.message}
        {...register('password')}
      />
      <Input
        label="Confirm Password"
        type={showPassword ? 'text' : 'password'}
        placeholder="Confirm your password"
        icon={<Lock className="h-4 w-4" />}
        error={errors.confirm_password?.message}
        {...register('confirm_password')}
      />
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="show-password"
          className="rounded border-input"
          onChange={() => setShowPassword(!showPassword)}
        />
        <label htmlFor="show-password" className="text-sm text-muted-foreground">
          Show passwords
        </label>
      </div>
      <Button type="submit" className="w-full" loading={isRegistering}>
        Create Account
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link href="/auth/login" className="text-primary hover:underline font-medium">
          Sign In
        </Link>
      </p>
    </form>
  )
}
