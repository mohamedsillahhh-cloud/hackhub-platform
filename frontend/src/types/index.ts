// =============================================================================
// Enums que correspondem ao backend
// =============================================================================

export enum EventStatus {
  DRAFT = 'draft',
  PUBLISHED = 'published',
  IN_PROGRESS = 'in_progress',
  CLOSED = 'closed',
}

export enum UserRole {
  ADMIN = 'admin',
  ORGANIZER = 'organizer',
  JUDGE = 'judge',
  PARTICIPANT = 'participant',
}

export enum TeamMemberRole {
  LEADER = 'leader',
  MEMBER = 'member',
}

export enum ProjectStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  FINALIZED = 'finalized',
}

export enum CertificateType {
  PARTICIPATION = 'participation',
  FINALIST = 'finalist',
  WINNER = 'winner',
  JUDGE = 'judge',
  ORGANIZER = 'organizer',
}

export enum NotificationCategory {
  TEAM_INVITE = 'team_invite',
  REGISTRATION_APPROVED = 'registration_approved',
  NEW_CHALLENGE = 'new_challenge',
  RESULT_PUBLISHED = 'result_published',
}

// =============================================================================
// Interfaces principais
// =============================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  hashed_password?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  bio?: string;
  university?: string;
  course?: string;
  country?: string;
  skills: string[];
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  experience_level?: string;
  preferred_languages: string[];
  preferred_frameworks: string[];
  interest_areas: string[];
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  title: string;
  description?: string;
  cover_image?: string;
  start_date: string;
  end_date: string;
  location?: string;
  is_online: boolean;
  status: EventStatus;
  regulations?: string;
  schedule?: Record<string, unknown>;
  sponsors?: Record<string, unknown>;
  prizes?: Record<string, unknown>;
  faq?: Record<string, unknown>;
  max_team_size: number;
  min_team_size: number;
  organizer_id: string;
  organizer?: User;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: string;
  name: string;
  description?: string;
  event_id: string;
  event?: Event;
  leader_id: string;
  leader?: User;
  members: TeamMember[];
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  user: User;
  role: TeamMemberRole;
  status: 'pending' | 'accepted' | 'rejected';
  invited_by?: string;
  created_at: string;
}

export interface Challenge {
  id: string;
  title: string;
  description?: string;
  requirements?: string;
  documentation_url?: string;
  event_id: string;
  category_id?: string;
  category?: ChallengeCategory;
  created_at: string;
}

export interface ChallengeCategory {
  id: string;
  name: string;
  description?: string;
  event_id: string;
  order: number;
  challenges?: Challenge[];
  criteria?: Criterion[];
  created_at: string;
}

export interface Criterion {
  id: string;
  name: string;
  description?: string;
  challenge_category_id: string;
  max_score: number;
  weight: number;
  created_at: string;
}

export interface Project {
  id: string;
  team_id: string;
  team?: Team;
  event_id: string;
  challenge_id?: string;
  name: string;
  description: string;
  github_url?: string;
  demo_video_url?: string;
  presentation_url?: string;
  tech_stack: string[];
  status: ProjectStatus;
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Evaluation {
  id: string;
  project_id: string;
  project?: Project;
  judge_id: string;
  judge?: User;
  comment?: string;
  total_score: number;
  scores: EvaluationScore[];
  submitted_at: string;
}

export interface EvaluationScore {
  id: string;
  evaluation_id: string;
  criterion_id: string;
  criterion?: Criterion;
  score: number;
  created_at: string;
}

export interface Certificate {
  id: string;
  user_id: string;
  user?: User;
  event_id: string;
  event?: Event;
  type: CertificateType;
  template_name: string;
  qr_code_url?: string;
  verification_code: string;
  digital_signature?: string;
  issued_at: string;
  extra_data?: Record<string, unknown>;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  category: NotificationCategory;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  read: boolean;
  sent_at: string;
  read_at?: string;
}

// =============================================================================
// Auth
// =============================================================================

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// =============================================================================
// Pagination
// =============================================================================

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

// =============================================================================
// Ranking
// =============================================================================

export interface RankingEntry {
  position: number;
  team_id?: string;
  team_name?: string;
  project_id?: string;
  project_name?: string;
  total_score: number;
  scores: Record<string, number>;
}

// =============================================================================
// Dashboard
// =============================================================================

export interface DashboardStats {
  total_users: number;
  active_participants: number;
  total_events: number;
  total_projects: number;
  total_teams: number;
  universities: number;
  countries: number;
  top_technologies: { name: string; count: number }[];
  events_by_status: Record<string, number>;
  recent_events: Array<{
    id: string;
    title: string;
    status: string;
    start_date: string;
    end_date: string;
  }>;
}

export interface EventDashboardStats {
  total_teams: number;
  total_projects: number;
  total_participants: number;
  projects_submitted: number;
  ranking: RankingEntry[];
}

// =============================================================================
// Request DTOs
// =============================================================================

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface CreateEventRequest {
  title: string;
  description?: string;
  cover_image?: string;
  start_date: string;
  end_date: string;
  location?: string;
  is_online?: boolean;
  regulations?: string;
  sponsors?: Record<string, unknown>;
  prizes?: Record<string, unknown>;
  faq?: Record<string, unknown>;
  max_team_size?: number;
  min_team_size?: number;
}

export interface CreateTeamRequest {
  name: string;
  description?: string;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
  github_url?: string;
  demo_video_url?: string;
  presentation_url?: string;
  tech_stack: string[];
  challenge_id?: string;
}

export interface CreateChallengeRequest {
  title: string;
  description?: string;
  requirements?: string;
  documentation_url?: string;
  category_id?: string;
}

export interface SubmitEvaluationRequest {
  project_id: string;
  scores: { criterion_id: string; score: number }[];
  comment?: string;
}

export interface AIAskRequest {
  question: string;
}

export interface AIEvaluateRequest {
  project_description?: string;
}

export interface AISuggestTeamsRequest {
  event_id: string;
}
