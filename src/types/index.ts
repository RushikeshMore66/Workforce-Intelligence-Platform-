// ============================================================
// ENUMS / UNION TYPES
// ============================================================

export type UserRole = 'OWNER' | 'SUPERVISOR' | 'TEAM_LEADER' | 'WORKER';

export type ProjectStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'DELAYED';
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'BLOCKED';

export type BlockerStatus = 'OPEN' | 'RESOLVED';

export type WorkerStatus = 'ACTIVE' | 'ON_LEAVE' | 'UNAVAILABLE';

export type NotificationType =
  | 'PROJECT_ALERT'
  | 'BLOCKER'
  | 'DEADLINE'
  | 'TEAM_UPDATE'
  | 'SYSTEM';

export type ReportType =
  | 'WEEKLY_WORKFORCE'
  | 'PROJECT_PROGRESS'
  | 'TEAM_PERFORMANCE'
  | 'BLOCKED_WORK'
  | 'SUPERVISOR_SUMMARY'
  | 'COMPANY_OVERVIEW';

// ============================================================
// USER
// ============================================================

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarInitials: string;
  company?: string; // for OWNER
}

export interface CurrentUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  company: string;
  avatarInitials: string;
}

// ============================================================
// SUPERVISOR
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
// ============================================================

export interface TeamLeader {
  id: string;
  userId: string;
  name: string;
  email: string;
  avatarInitials: string;
  teamId: string;
}

export interface Team {
  id: string;
  name: string;
  supervisorId: string;
  teamLeaderId: string;
  memberCount: number;
  projectIds: string[];
}

// ============================================================
// WORKER
// ============================================================

export interface Worker {
  id: string;
  name: string;
  email: string;
  role: string; // e.g. "Senior Backend Developer"
  teamId: string;
  teamLeaderId: string;
  supervisorId: string;
  avatarInitials: string;
  status: WorkerStatus;
  activeProjectId: string | null;
  completedTaskCount: number;
  inProgressTaskCount: number;
  pendingTaskCount: number;
  blockedTaskCount: number;
}

// ============================================================
// PROJECT
// ============================================================

export interface Project {
  id: string;
  name: string;
  client: string;
  description: string;
  startDate: string;       // ISO date string
  deadline: string;        // ISO date string
  priority: ProjectPriority;
  supervisorId: string;
  // System-maintained
  status: ProjectStatus;
  health: ProjectHealth;
  progress: number;        // 0–100
  teamCount: number;
  createdAt: string;       // ISO datetime
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
// ============================================================

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  assigneeId: string;
  teamId: string;
  status: TaskStatus;
  priority: ProjectPriority;
  dueDate: string;
  createdAt: string;
}

// ============================================================
// WORK UPDATE
// ============================================================

export interface WorkUpdate {
  id: string;
  taskId: string;
  workerId: string;
  description: string;
  timestamp: string;
}

// ============================================================
// BLOCKER
// ============================================================

export interface Blocker {
  id: string;
  projectId: string;
  taskId?: string;
  title: string;
  description: string;
  reportedById: string;    // worker or team leader
  teamId: string;
  createdDate: string;
  resolvedDate?: string;
  status: BlockerStatus;
}

// ============================================================
// PROJECT ACTIVITY
// ============================================================

export interface ProjectActivity {
  id: string;
  projectId: string;
  description: string;
  userId: string;
  userName: string;
  timestamp: string;
  type: 'TASK_COMPLETED' | 'TASK_UPDATED' | 'BLOCKER_REPORTED' | 'BLOCKER_RESOLVED' | 'PROJECT_UPDATED' | 'MEMBER_ADDED';
}

// ============================================================
// NOTIFICATION
// ============================================================

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  projectId?: string;
  read: boolean;
  timestamp: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
}

// ============================================================
// ATTENTION ITEM (Dashboard)
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
