// ============================================================
// ENUMS / UNION TYPES
// These mirror the backend Python enums exactly.
// DO NOT use magic strings elsewhere — always import from here.
// ============================================================

export type UserRole = 'OWNER' | 'SUPERVISOR' | 'TEAM_LEADER' | 'WORKER';

export type ProjectStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'DELAYED';
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED';

// Backend BlockerStatusEnum: OPEN | RESOLVED
export type BlockerStatus = 'OPEN' | 'RESOLVED';

export type WorkerStatus = 'ACTIVE' | 'ON_LEAVE' | 'UNAVAILABLE';

// All 15 event types from backend ActivityTypeEnum
export type ActivityType =
  | 'PROJECT_CREATED'
  | 'PROJECT_UPDATED'
  | 'PROJECT_STATUS_CHANGED'
  | 'PROJECT_ASSIGNED'
  | 'TASK_CREATED'
  | 'TASK_UPDATED'
  | 'TASK_ASSIGNED'
  | 'TASK_STATUS_CHANGED'
  | 'TASK_COMPLETED'
  | 'WORK_UPDATE_ADDED'
  | 'BLOCKER_REPORTED'
  | 'BLOCKER_RESOLVED'
  | 'TEAM_CREATED'
  | 'TEAM_UPDATED'
  | 'MEMBER_ADDED'
  | 'MEMBER_REMOVED'
  | 'USER_CREATED'
  | 'USER_UPDATED';

// All 7 types from backend NotificationTypeEnum
export type NotificationType =
  | 'PROJECT_ALERT'
  | 'BLOCKER'
  | 'DEADLINE'
  | 'TASK'
  | 'WORK_UPDATE'
  | 'TEAM_UPDATE'
  | 'SYSTEM';

// All 4 priorities from backend NotificationPriorityEnum
export type NotificationPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export type ReportType =
  | 'WEEKLY_WORKFORCE'
  | 'PROJECT_PROGRESS'
  | 'TEAM_PERFORMANCE'
  | 'BLOCKED_WORK'
  | 'SUPERVISOR_SUMMARY'
  | 'COMPANY_OVERVIEW';

// ============================================================
// USER
// Merged from User + CurrentUser (were identical shapes).
// Matches backend UserOut schema.
// ============================================================

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarInitials: string;
  company?: string; // present for OWNER role
}

/** @deprecated Use User directly. Kept for compatibility during migration. */
export type CurrentUser = User & { company: string };

// ============================================================
// SUPERVISOR
// Matches backend SupervisorOut schema.
// name/email/avatarInitials are embedded from the related User.
// ============================================================

export interface Supervisor {
  id: string;
  userId: string;
  name: string;
  email: string;
  avatarInitials: string;
  projectIds: string[];
  teamIds: string[];
}

// ============================================================
// TEAM
// Matches backend Team model.
// memberCount is a display-only derived value — not a backend field.
// projectIds is derived from the M2M teams<->projects relationship.
// ============================================================

export interface TeamLeader {
  id: string;
  userId: string;
  name: string;
  email: string;
  avatarInitials: string;
  teamId: string | null;
}

export interface Team {
  id: string;
  name: string;
  supervisorId: string;
  teamLeaderId?: string; // derived from TeamLeader.team_id
  // Display-only derived values — do NOT treat as authoritative source of truth
  memberCount?: number;
  projectIds?: string[];
}

// ============================================================
// WORKER
// Matches backend WorkerOut schema.
// Task counts are derived display values from backend aggregation.
// ============================================================

export interface Worker {
  id: string;
  name: string;
  email: string;
  role: string; // job title, e.g. "Senior Backend Developer"
  teamId: string | null;
  teamLeaderId: string | null;
  supervisorId: string | null;
  avatarInitials: string;
  status: WorkerStatus;
  activeProjectId: string | null;
  // Derived aggregate display values (computed by backend from tasks)
  completedTaskCount: number;
  inProgressTaskCount: number;
  pendingTaskCount: number;
  blockedTaskCount: number;
}

// ============================================================
// PROJECT
// Matches backend Project model / ProjectOut schema.
// teamCount is a derived display value — not stored by backend.
// ============================================================

export interface Project {
  id: string;
  name: string;
  client: string;
  description: string;
  startDate: string;       // ISO date string
  deadline: string;        // ISO date string
  priority: ProjectPriority;
  supervisorId: string | null;
  status: ProjectStatus;
  health: ProjectHealth;
  progress: number;        // 0–100, maintained by backend service layer
  createdAt: string;       // ISO datetime string
  updatedAt?: string;      // ISO datetime string
  // Display-only derived value — backend returns teams[] count
  teamCount?: number;
}

export interface CreateProjectInput {
  name: string;
  client: string;
  description: string;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string;
}

export interface UpdateProjectInput extends Partial<CreateProjectInput> {
  status?: ProjectStatus;
  health?: ProjectHealth;
  progress?: number;
}

// ============================================================
// TASK
// Matches backend Task model / TaskOut schema.
// ============================================================

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  assigneeId: string | null;
  teamId: string | null;
  status: TaskStatus;
  priority: ProjectPriority;
  dueDate: string;         // ISO date string
  createdAt: string;       // ISO datetime string
  updatedAt?: string;      // ISO datetime string
}

export interface CreateTaskInput {
  projectId: string;
  title: string;
  description?: string;
  assigneeId?: string;
  teamId?: string;
  priority: ProjectPriority;
  dueDate: string;
}

export interface UpdateTaskInput extends Partial<CreateTaskInput> {
  status?: TaskStatus;
}

// ============================================================
// WORK UPDATE
// Matches backend WorkUpdate model.
// ============================================================

export interface WorkUpdate {
  id: string;
  taskId: string;
  workerId: string;
  description: string;
  timestamp: string;       // ISO datetime string
}

export interface CreateWorkUpdateInput {
  taskId: string;
  description: string;
}

// ============================================================
// BLOCKER
// Matches backend Blocker model.
// ============================================================

export interface Blocker {
  id: string;
  projectId: string;
  taskId?: string | null;
  title: string;
  description: string;
  reportedById: string | null;
  teamId: string | null;
  createdDate: string;     // ISO date string
  resolvedDate?: string | null;
  status: BlockerStatus;
}

export interface CreateBlockerInput {
  projectId: string;
  taskId?: string;
  title: string;
  description: string;
  teamId?: string;
}

// ============================================================
// PROJECT ACTIVITY
// Matches backend ProjectActivity model.
// All 18 ActivityType values are now represented.
// ============================================================

export interface ProjectActivity {
  id: string;
  projectId: string;
  description: string;
  userId: string | null;
  userName: string;         // snapshot of name at event time
  timestamp: string;        // ISO datetime string
  type: ActivityType;
}

// ============================================================
// NOTIFICATION
// Matches backend Notification model.
// All 7 NotificationType and 4 NotificationPriority values included.
// ============================================================

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  projectId?: string | null;
  read: boolean;
  timestamp: string;        // ISO datetime string
  priority: NotificationPriority;
}

// ============================================================
// ATTENTION ITEM (Dashboard — frontend-only abstraction)
// Will eventually come from an Intelligence or Dashboard API endpoint.
// ============================================================

export interface AttentionItem {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  projectId?: string;
  type: 'RISK' | 'DEADLINE' | 'BLOCKER' | 'OVERLOAD' | 'REVIEW';
}

// ============================================================
// DASHBOARD
// Will come from a backend aggregate endpoint.
// ============================================================

export interface DashboardMetrics {
  activeProjects: number;
  completedProjects: number;
  totalWorkers: number;
  workersActive: number;
  workersOnLeave: number;
  workersUnavailable: number;
  tasksCompleted: number;
  tasksInProgress: number;
  tasksPending: number;
  tasksBlocked: number;
  projectsOnTrack: number;
  projectsAtRisk: number;
  projectsDelayed: number;
}

// ============================================================
// ANALYTICS
// Will come from a backend analytics aggregate endpoint.
// ============================================================

export interface TaskCompletionDataPoint {
  month: string;
  completed: number;
  inProgress: number;
  blocked: number;
}

export interface TeamWorkloadDataPoint {
  team: string;
  tasks: number;
  completed: number;
  blocked: number;
}

export interface ProjectProgressDataPoint {
  name: string;
  progress: number;
  target: number;
}

export interface WorkloadTrendPoint {
  week: string;
  backend: number;
  frontend: number;
  qa: number;
  devops: number;
  uiux: number;
}

export interface AnalyticsData {
  taskCompletion: TaskCompletionDataPoint[];
  teamWorkload: TeamWorkloadDataPoint[];
  projectProgress: ProjectProgressDataPoint[];
  workloadTrend: WorkloadTrendPoint[];
}

// ============================================================
// REPORTS
// Will come from a backend report generation endpoint.
// ============================================================

export interface ReportFilter {
  type: ReportType;
  startDate: string;
  endDate: string;
  projectId?: string;
  teamId?: string;
}

export interface Report {
  id: string;
  type: ReportType;
  title: string;
  generatedAt: string;
  filter: ReportFilter;
  sections: ReportSection[];
}

export interface ReportSection {
  title: string;
  content: string;
  data?: Record<string, number | string>[];
}

// ============================================================
// AUTH
// Used by AuthProvider and useAuth hook.
// ============================================================

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  accessToken: string;
  tokenType: string;
}

// ============================================================
// API RESPONSE WRAPPERS
// Common envelope shapes returned by the FastAPI backend.
// ============================================================

export interface ApiError {
  success: false;
  error: string;
  detail: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
