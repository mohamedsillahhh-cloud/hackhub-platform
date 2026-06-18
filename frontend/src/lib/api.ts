import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type {
  LoginRequest, RegisterRequest, User, Event, Team, TeamMember,
  Challenge, ChallengeCategory, Criterion, Project, Evaluation,
  EvaluationScore, Certificate, Notification, AuthTokens,
  PaginatedResponse, RankingEntry, DashboardStats, EventDashboardStats,
  CreateEventRequest, CreateTeamRequest, CreateProjectRequest,
  CreateChallengeRequest, SubmitEvaluationRequest, AIAskRequest,
  AIEvaluateRequest, AISuggestTeamsRequest,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (typeof window !== 'undefined') {
    const tokens = localStorage.getItem('auth_tokens')
    if (tokens) {
      const parsed: AuthTokens = JSON.parse(tokens)
      config.headers.Authorization = `Bearer ${parsed.access_token}`
    }
  }
  return config
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const tokens = localStorage.getItem('auth_tokens')
        if (!tokens) throw new Error('No tokens')

        const parsed: AuthTokens = JSON.parse(tokens)
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: parsed.refresh_token,
        })

        const newTokens: AuthTokens = response.data
        localStorage.setItem('auth_tokens', JSON.stringify(newTokens))
        api.defaults.headers.common.Authorization = `Bearer ${newTokens.access_token}`
        processQueue(null, newTokens.access_token)

        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError, null)
        localStorage.removeItem('auth_tokens')
        if (typeof window !== 'undefined') {
          window.location.href = '/auth/login'
        }
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)

const apiClient = {
  auth: {
    login: (data: LoginRequest) =>
      api.post<AuthTokens>('/auth/login', data).then((r) => r.data),
    register: (data: RegisterRequest) =>
      api.post<User>('/auth/register', data).then((r) => r.data),
    refresh: (refreshToken: string) =>
      api.post<AuthTokens>('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data),
    verifyEmail: (token: string) =>
      api.post('/auth/verify-email', { token }).then((r) => r.data),
    resetPassword: (email: string) =>
      api.post('/auth/reset-password', { email }).then((r) => r.data),
    confirmReset: (token: string, password: string) =>
      api.post('/auth/confirm-reset', { token, password }).then((r) => r.data),
    getMe: () =>
      api.get<User>('/auth/me').then((r) => r.data),
    updateProfile: (data: Partial<User>) =>
      api.patch<User>('/auth/me', data).then((r) => r.data),
  },

  events: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Event>>('/events', { params }).then((r) => r.data),
    getById: (id: string) =>
      api.get<Event>(`/events/${id}`).then((r) => r.data),
    create: (data: CreateEventRequest) =>
      api.post<Event>('/events', data).then((r) => r.data),
    update: (id: string, data: Partial<CreateEventRequest>) =>
      api.patch<Event>(`/events/${id}`, data).then((r) => r.data),
    delete: (id: string) =>
      api.delete(`/events/${id}`).then((r) => r.data),
    changeStatus: (id: string, status: string) =>
      api.patch<Event>(`/events/${id}/status`, { status }).then((r) => r.data),
  },

  teams: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Team>>('/teams', { params }).then((r) => r.data),
    create: (data: CreateTeamRequest) =>
      api.post<Team>('/teams', data).then((r) => r.data),
    invite: (teamId: string, emailOrUsername: string) =>
      api.post(`/teams/${teamId}/invite`, { email_or_username: emailOrUsername }).then((r) => r.data),
    join: (inviteCode: string) =>
      api.post<Team>('/teams/join', { invite_code: inviteCode }).then((r) => r.data),
    accept: (teamId: string) =>
      api.post(`/teams/${teamId}/accept`).then((r) => r.data),
    reject: (teamId: string) =>
      api.post(`/teams/${teamId}/reject`).then((r) => r.data),
    removeMember: (teamId: string, userId: string) =>
      api.delete(`/teams/${teamId}/members/${userId}`).then((r) => r.data),
    leave: (teamId: string) =>
      api.post(`/teams/${teamId}/leave`).then((r) => r.data),
    getById: (id: string) =>
      api.get<Team>(`/teams/${id}`).then((r) => r.data),
  },

  challenges: {
    list: (eventId: string) =>
      api.get<Challenge[]>(`/events/${eventId}/challenges`).then((r) => r.data),
    create: (data: CreateChallengeRequest) =>
      api.post<Challenge>('/challenges', data).then((r) => r.data),
    getById: (id: string) =>
      api.get<Challenge>(`/challenges/${id}`).then((r) => r.data),
    update: (id: string, data: Partial<CreateChallengeRequest>) =>
      api.patch<Challenge>(`/challenges/${id}`, data).then((r) => r.data),
    delete: (id: string) =>
      api.delete(`/challenges/${id}`).then((r) => r.data),
    createCategory: (eventId: string, data: { name: string; description?: string }) =>
      api.post<ChallengeCategory>(`/events/${eventId}/categories`, data).then((r) => r.data),
    listCategories: (eventId: string) =>
      api.get<ChallengeCategory[]>(`/events/${eventId}/categories`).then((r) => r.data),
    createCriterion: (challengeId: string, data: Omit<Criterion, 'id' | 'challenge_id' | 'created_at'>) =>
      api.post<Criterion>(`/challenges/${challengeId}/criteria`, data).then((r) => r.data),
  },

  projects: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Project>>('/projects', { params }).then((r) => r.data),
    create: (data: CreateProjectRequest) =>
      api.post<Project>('/projects', data).then((r) => r.data),
    getById: (id: string) =>
      api.get<Project>(`/projects/${id}`).then((r) => r.data),
    update: (id: string, data: Partial<CreateProjectRequest>) =>
      api.patch<Project>(`/projects/${id}`, data).then((r) => r.data),
    submit: (id: string) =>
      api.post<Project>(`/projects/${id}/submit`).then((r) => r.data),
  },

  evaluations: {
    submit: (data: SubmitEvaluationRequest) =>
      api.post<Evaluation>('/evaluations', data).then((r) => r.data),
    getProjectEvaluations: (projectId: string) =>
      api.get<Evaluation[]>(`/projects/${projectId}/evaluations`).then((r) => r.data),
    getRanking: (eventId: string) =>
      api.get<RankingEntry[]>(`/events/${eventId}/ranking`).then((r) => r.data),
    getMyEvaluations: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Evaluation>>('/evaluations/me', { params }).then((r) => r.data),
  },

  ranking: {
    getFullRanking: (eventId: string) =>
      api.get<RankingEntry[]>(`/events/${eventId}/ranking`).then((r) => r.data),
  },

  users: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<User>>('/users', { params }).then((r) => r.data),
    getById: (id: string) =>
      api.get<User>(`/users/${id}`).then((r) => r.data),
    getCertificates: (userId: string) =>
      api.get<Certificate[]>(`/users/${userId}/certificates`).then((r) => r.data),
  },

  certificates: {
    verify: (hash: string) =>
      api.get<Certificate>(`/certificates/verify/${hash}`).then((r) => r.data),
    download: (id: string) =>
      api.get(`/certificates/${id}/download`, { responseType: 'blob' }).then((r) => r.data),
  },

  notifications: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Notification>>('/notifications', { params }).then((r) => r.data),
    markRead: (id: string) =>
      api.patch(`/notifications/${id}/read`).then((r) => r.data),
    markAllRead: () =>
      api.post('/notifications/read-all').then((r) => r.data),
  },

  ai: {
    ask: (data: AIAskRequest) =>
      api.post<{ answer: string }>('/ai/ask', data).then((r) => r.data),
    evaluateProject: (data: AIEvaluateRequest) =>
      api.post<{ scores: Record<string, number>; feedback: string }>('/ai/evaluate', data).then((r) => r.data),
    suggestTeams: (data: AISuggestTeamsRequest) =>
      api.post<{ teams: { name: string; members: string[] }[] }>('/ai/suggest-teams', data).then((r) => r.data),
  },

  dashboard: {
    getStats: () =>
      api.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
    getEventStats: (eventId: string) =>
      api.get<EventDashboardStats>(`/dashboard/events/${eventId}/stats`).then((r) => r.data),
  },
}

export { api, apiClient }
export default apiClient
