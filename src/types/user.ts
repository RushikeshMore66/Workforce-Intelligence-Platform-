export type UserRole = 'OWNER' | 'SUPERVISOR' | 'TEAM_LEADER' | 'WORKER';

export type WorkerStatus = 'ACTIVE' | 'ON_LEAVE' | 'UNAVAILABLE';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  avatarInitials: string;
  company?: string;
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
