export type UserRole = 'OWNER' | 'SUPERVISOR' | 'TEAM_LEADER' | 'WORKER';

export type WorkerStatus = 'ACTIVE' | 'ON_LEAVE' | 'UNAVAILABLE';

/** Account lifecycle state — separate from WorkerStatus which is operational. */
export type AccountStatus = 'ACTIVE' | 'DEACTIVATED';

/** Core authenticated user — returned from /auth/me */
export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarInitials: string;
  company?: string;
  /** Account lifecycle — false means the user cannot login */
  isActive: boolean;
  /** Role-profile IDs: populated based on role. Avoid email-based profile scanning. */
  workerProfileId?: string | null;
  supervisorProfileId?: string | null;
  teamLeaderProfileId?: string | null;
}

/** Full user record returned from the management API (owner-facing) */
export interface ManagedUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatarInitials: string;
  company?: string;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  workerProfileId?: string | null;
  supervisorProfileId?: string | null;
  teamLeaderProfileId?: string | null;
}

export interface Supervisor {
  id: string;
  userId: string;
  name: string;
  email: string;
  avatarInitials: string;
  projectIds: string[];
  teamIds: string[];
}

export interface TeamLeader {
  id: string;
  userId: string;
  name: string;
  email: string;
  avatarInitials: string;
  teamId: string | null;
}

export interface Worker {
  id: string;
  name: string;
  email: string;
  role: string;
  teamId: string | null;
  teamLeaderId: string | null;
  supervisorId: string | null;
  avatarInitials: string;
  status: WorkerStatus;
  activeProjectId: string | null;
}

export interface WorkerMetrics {
  completedTaskCount: number;
  inProgressTaskCount: number;
  pendingTaskCount: number;
  blockedTaskCount: number;
}

export type WorkerViewModel = Worker & WorkerMetrics;

// ── User creation payload ──────────────────────────────────────────────────────

export interface WorkerProfileCreate {
  jobTitle: string;
  teamId?: string;
  teamLeaderId?: string;
  supervisorId?: string;
  status: WorkerStatus;
}

export interface TeamLeaderProfileCreate {
  teamId?: string;
}

export interface SupervisorProfileCreate {
  // Reserved for future expansion
}

export interface CreateUserPayload {
  email: string;
  name: string;
  password: string;
  role: UserRole;
  company?: string;
  avatarInitials?: string;
  workerProfile?: WorkerProfileCreate;
  teamLeaderProfile?: TeamLeaderProfileCreate;
  supervisorProfile?: SupervisorProfileCreate;
}

export interface UpdateUserPayload {
  name?: string;
  company?: string;
  avatarInitials?: string;
  role?: UserRole;
}

// ── Profile / password ─────────────────────────────────────────────────────────

export interface UpdateProfilePayload {
  name?: string;
  company?: string;
  avatarInitials?: string;
}

export interface ChangePasswordPayload {
  currentPassword: string;
  newPassword: string;
}
