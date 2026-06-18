export enum EventStatus {
  DRAFT = 'draft',
  UPCOMING = 'upcoming',
  ACTIVE = 'active',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export enum TeamMemberRole {
  LEADER = 'leader',
  CO_LEADER = 'co_leader',
  MEMBER = 'member',
}

export enum EvaluationStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  university?: string;
  course?: string;
  country?: string;
  skills: string[];
  github_url?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  role: 'participant' | 'organizer' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface Event {
  id: string;
  title: string;
  slug: string;
  description: string;
  short_description?: string;
  cover_image_url?: string;
  status: EventStatus;
  start_date: string;
  end_date: string;
  registration_deadline?: string;
  location?: string;
  is_remote: boolean;
  max_participants?: number;
  max_team_size: number;
  prizes?: string;
  sponsors?: string;
  rules?: string;
  organizer_id: string;
  organizer?: User;
  participant_count?: number;
  team_count?: number;
  project_count?: number;
  created_at: string;
  updated_at: string;
}

export interface Team {
  id: string;
  name: string;
  slug: string;
  description?: string;
  invite_code: string;
  event_id: string;
  event?: Event;
  leader_id: string;
  leader?: User;
  members: TeamMember[];
  project?: Project;
  member_count?: number;
  created_at: string;
  updated_at: string;
  is_registered?: boolean;
  registration_status?: 'pending' | 'approved' | 'rejected';
}

export interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  user: User;
  role: TeamMemberRole;
  created_at: string;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  category_id?: string;
  category?: ChallengeCategory;
  event_id: string;
  event?: Event;
  criteria: Criterion[];
  max_score: number;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface ChallengeCategory {
  id: string;
  name: string;
  description?: string;
  event_id: string;
  challenges?: Challenge[];
  created_at: string;
}

export interface Criterion {
  id: string;
  name: string;
  description?: string;
  max_score: number;
  weight: number;
  challenge_id: string;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  github_url?: string;
  demo_url?: string;
  video_url?: string;
  tech_stack: string[];
  team_id: string;
  team?: Team;
  event_id: string;
  event?: Event;
  challenge_id?: string;
  challenge?: Challenge;
  status: 'draft' | 'submitted' | 'evaluated' | 'disqualified';
  score?: number;
  rank?: number;
  evaluations?: Evaluation[];
  created_at: string;
  updated_at: string;
  submitted_at?: string;
}

export interface Evaluation {
  id: string;
  evaluator_id: string;
  evaluator?: User;
  project_id: string;
  project?: Project;
  challenge_id: string;
  challenge?: Challenge;
  scores: EvaluationScore[];
  total_score: number;
  comments?: string;
  status: EvaluationStatus;
  created_at: string;
  updated_at: string;
}

export interface EvaluationScore {
  id: string;
  criterion_id: string;
  criterion?: Criterion;
  evaluation_id: string;
  score: number;
  comment?: string;
  created_at: string;
}

export interface Certificate {
  id: string;
  user_id: string;
  user?: User;
  event_id: string;
  event?: Event;
  project_id?: string;
  project?: Project;
  type: 'participation' | 'winner' | 'finalist';
  certificate_url: string;
  certificate_hash: string;
  issued_at: string;
  created_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: Record<string, unknown>;
  read: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface RankingEntry {
  position: number;
  team: Team;
  project?: Project;
  total_score: number;
  scores: Record<string, number>;
}

export interface DashboardStats {
  total_users: number;
  total_events: number;
  active_events: number;
  total_teams: number;
  total_projects: number;
  total_participants: number;
  users_by_role: Record<string, number>;
  events_by_status: Record<string, number>;
  projects_by_status: Record<string, number>;
  recent_events: Event[];
  top_technologies: { name: string; count: number }[];
  participants_by_university: { university: string; count: number }[];
  users_over_time: { date: string; count: number }[];
}

export interface EventDashboardStats {
  total_teams: number;
  total_projects: number;
  total_participants: number;
  projects_submitted: number;
  projects_evaluated: number;
  pending_evaluations: number;
  top_teams: RankingEntry[];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
  confirm_password: string;
}

export interface CreateEventRequest {
  title: string;
  description: string;
  short_description?: string;
  cover_image_url?: string;
  start_date: string;
  end_date: string;
  registration_deadline?: string;
  location?: string;
  is_remote: boolean;
  max_participants?: number;
  max_team_size: number;
  prizes?: string;
  sponsors?: string;
  rules?: string;
}

export interface CreateTeamRequest {
  name: string;
  description?: string;
  event_id: string;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
  github_url?: string;
  demo_url?: string;
  video_url?: string;
  tech_stack: string[];
  team_id: string;
  event_id: string;
  challenge_id?: string;
}

export interface CreateChallengeRequest {
  title: string;
  description: string;
  category_id?: string;
  event_id: string;
  criteria: Omit<Criterion, 'id' | 'challenge_id' | 'created_at'>[];
  max_score: number;
  order: number;
}

export interface SubmitEvaluationRequest {
  project_id: string;
  challenge_id: string;
  scores: { criterion_id: string; score: number; comment?: string }[];
  comments?: string;
}

export interface AIAskRequest {
  question: string;
  event_id?: string;
}

export interface AIEvaluateRequest {
  project_description: string;
  criteria: { name: string; max_score: number }[];
}

export interface AISuggestTeamsRequest {
  event_id: string;
  participant_ids: string[];
}
