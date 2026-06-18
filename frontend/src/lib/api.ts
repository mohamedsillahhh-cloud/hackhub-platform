import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'
import type {
  LoginRequest, RegisterRequest, User, Event, Team, TeamMember,
  Challenge, ChallengeCategory, Criterion, Project, Evaluation,
  Certificate, Notification,
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
  withCredentials: true,
})

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
}> = []

const processQueue = (error: unknown) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(undefined)
    }
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh') {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => api(originalRequest))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await axios.post(`${API_URL}/auth/refresh`, {}, { withCredentials: true })
        processQueue(null)
        return api(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)
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
      api.post('/auth/login', data).then((r) => r.data),
    register: (data: RegisterRequest) =>
      api.post<User>('/auth/register', data).then((r) => r.data),
    refresh: () =>
      api.post('/auth/refresh').then((r) => r.data),
    logout: () =>
      api.post('/auth/logout').then((r) => r.data),
    verifyEmail: (token: string) =>
      api.post(`/auth/verify-email/${token}`).then((r) => r.data),
    resetPassword: (email: string) =>
      api.post('/auth/password-reset', { email }).then((r) => r.data),
    confirmReset: (token: string, password: string) =>
      api.post('/auth/password-reset/confirm', { token, password }).then((r) => r.data),
    getMe: () =>
      api.get<User>('/auth/me').then((r) => r.data),
    updateProfile: (data: Partial<User>) =>
      api.put<User>('/auth/me', data).then((r) => r.data),
  },

  events: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Event>>('/events', { params }).then((r) => r.data),
    getById: (id: string) =>
      api.get<Event>(`/events/${id}`).then((r) => r.data),
    create: (data: CreateEventRequest) =>
      api.post<Event>('/events', data).then((r) => r.data),
    update: (id: string, data: Partial<CreateEventRequest>) =>
      api.put<Event>(`/events/${id}`, data).then((r) => r.data),
    delete: (id: string) =>
      api.delete(`/events/${id}`).then((r) => r.data),
    changeStatus: (id: string, status: string) =>
      api.patch<Event>(`/events/${id}/status`, { status }).then((r) => r.data),
  },

  teams: {
    list: (eventId: string) =>
      api.get<Team[]>(`/events/${eventId}/teams`).then((r) => r.data),
    create: (eventId: string, data: CreateTeamRequest) =>
      api.post<Team>(`/events/${eventId}/teams`, data).then((r) => r.data),
    getById: (eventId: string, teamId: string) =>
      api.get<Team>(`/events/${eventId}/teams/${teamId}`).then((r) => r.data),
    getByIdStandalone: (teamId: string) =>
      api.get<Team>(`/teams/${teamId}`).then((r) => r.data),
    listMyTeams: () =>
      api.get<Team[]>('/teams').then((r) => r.data),
    invite: (eventId: string, teamId: string, userId: string) =>
      api.post<TeamMember>(`/events/${eventId}/teams/${teamId}/invite`, { user_id: userId }).then((r) => r.data),
    join: (eventId: string, inviteCode: string) =>
      api.post<Team>(`/events/${eventId}/teams/join`, { invitation_code: inviteCode }).then((r) => r.data),
    accept: (eventId: string, teamId: string, memberId: string) =>
      api.post(`/events/${eventId}/teams/${teamId}/accept/${memberId}`).then((r) => r.data),
    reject: (eventId: string, teamId: string, memberId: string) =>
      api.post(`/events/${eventId}/teams/${teamId}/reject/${memberId}`).then((r) => r.data),
    removeMember: (eventId: string, teamId: string, memberId: string) =>
      api.delete(`/events/${eventId}/teams/${teamId}/members/${memberId}`).then((r) => r.data),
    leave: (eventId: string, teamId: string) =>
      api.delete(`/events/${eventId}/teams/${teamId}/leave`).then((r) => r.data),
  },

  challenges: {
    list: (eventId: string) =>
      api.get<Challenge[]>(`/events/${eventId}/challenges`).then((r) => r.data),
    create: (eventId: string, data: CreateChallengeRequest) =>
      api.post<Challenge>(`/events/${eventId}/challenges`, data).then((r) => r.data),
    getById: (eventId: string, challengeId: string) =>
      api.get<Challenge>(`/events/${eventId}/challenges/${challengeId}`).then((r) => r.data),
    update: (eventId: string, challengeId: string, data: Partial<CreateChallengeRequest>) =>
      api.put<Challenge>(`/events/${eventId}/challenges/${challengeId}`, data).then((r) => r.data),
    delete: (eventId: string, challengeId: string) =>
      api.delete(`/events/${eventId}/challenges/${challengeId}`).then((r) => r.data),
    listCategories: (eventId: string) =>
      api.get<ChallengeCategory[]>(`/events/${eventId}/challenges/categories`).then((r) => r.data),
    createCategory: (eventId: string, data: { name: string; description?: string }) =>
      api.post<ChallengeCategory>(`/events/${eventId}/challenges/categories`, data).then((r) => r.data),
    createCriterion: (eventId: string, data: { category_id: string; name: string; max_score: number; weight: number }) =>
      api.post<Criterion>(`/events/${eventId}/challenges/criteria`, data).then((r) => r.data),
  },

  projects: {
    list: (eventId: string, params?: Record<string, unknown>) =>
      api.get<Project[]>(`/events/${eventId}/projects`, { params }).then((r) => r.data),
    create: (eventId: string, data: CreateProjectRequest) =>
      api.post<Project>(`/events/${eventId}/projects`, data).then((r) => r.data),
    getById: (eventId: string, projectId: string) =>
      api.get<Project>(`/events/${eventId}/projects/${projectId}`).then((r) => r.data),
    update: (eventId: string, projectId: string, data: Partial<CreateProjectRequest>) =>
      api.put<Project>(`/events/${eventId}/projects/${projectId}`, data).then((r) => r.data),
    submit: (eventId: string, projectId: string) =>
      api.post(`/events/${eventId}/projects/${projectId}/submit`).then((r) => r.data),
  },

  evaluations: {
    submit: (eventId: string, data: SubmitEvaluationRequest) =>
      api.post<Evaluation>(`/events/${eventId}/evaluations`, data).then((r) => r.data),
    getProjectEvaluations: (eventId: string, projectId: string) =>
      api.get<Evaluation[]>(`/events/${eventId}/evaluations/projects/${projectId}`).then((r) => r.data),
    getRanking: (eventId: string) =>
      api.get<RankingEntry[]>(`/events/${eventId}/evaluations/ranking`).then((r) => r.data),
    getMyEvaluations: (eventId: string) =>
      api.get<Evaluation[]>(`/events/${eventId}/evaluations/my`).then((r) => r.data),
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
    list: () =>
      api.get<Certificate[]>('/certificates/my').then((r) => r.data),
    verify: (code: string) =>
      api.get<Certificate>(`/certificates/verify/${code}`).then((r) => r.data),
    download: (id: string) =>
      api.get(`/certificates/download/${id}`, { responseType: 'blob' }).then((r) => r.data),
    generate: (eventId: string) =>
      api.post(`/certificates/events/${eventId}/generate`).then((r) => r.data),
  },

  notifications: {
    list: (params?: Record<string, unknown>) =>
      api.get<PaginatedResponse<Notification>>('/notifications', { params }).then((r) => r.data),
    markRead: (id: string) =>
      api.put(`/notifications/${id}/read`).then((r) => r.data),
    markAllRead: () =>
      api.put('/notifications/read-all').then((r) => r.data),
  },

  ai: {
    ask: (eventId: string, data: AIAskRequest) =>
      api.post<{ answer: string }>(`/ai/events/${eventId}/ask`, data).then((r) => r.data),
    evaluateProject: (projectId: string) =>
      api.post<{ scores: Record<string, number>; feedback: string }>(`/ai/evaluate/${projectId}`).then((r) => r.data),
    suggestTeams: (eventId: string) =>
      api.post<{ teams: { members: string[]; combined_skills: string[] }[] }>(`/ai/events/${eventId}/suggest-teams`).then((r) => r.data),
  },

  dashboard: {
    getStats: () =>
      api.get<DashboardStats>('/dashboard/stats').then((r) => r.data),
    getEventStats: (eventId: string) =>
      api.get<EventDashboardStats>(`/dashboard/events/${eventId}/stats`).then((r) => r.data),
    exportParticipants: (eventId: string, fmt: string = 'xlsx') =>
      api.get(`/dashboard/events/${eventId}/export/participants?fmt=${fmt}`, { responseType: 'blob' }).then((r) => r.data),
    exportProjects: (eventId: string, fmt: string = 'xlsx') =>
      api.get(`/dashboard/events/${eventId}/export/projects?fmt=${fmt}`, { responseType: 'blob' }).then((r) => r.data),
    exportRanking: (eventId: string, fmt: string = 'xlsx') =>
      api.get(`/dashboard/events/${eventId}/export/ranking?fmt=${fmt}`, { responseType: 'blob' }).then((r) => r.data),
    exportEvaluations: (eventId: string, fmt: string = 'xlsx') =>
      api.get(`/dashboard/events/${eventId}/export/evaluations?fmt=${fmt}`, { responseType: 'blob' }).then((r) => r.data),
  },
}

export { api, apiClient }
export default apiClient
