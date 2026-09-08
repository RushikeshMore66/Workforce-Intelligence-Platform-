export type ProjectStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'DELAYED';
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Project {
  id: string;
  name: string;
  client: string;
  description: string | null;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string | null;
  status: ProjectStatus;
  health: ProjectHealth;
  progress: number;
  teamCount: number;
  createdAt: string;
}

export interface ProjectDetail extends Project {
  teamIds: string[];
}

// Alias for backwards compatibility with existing UI if needed, though Project itself now covers it
export type ProjectViewModel = Project;

export interface CreateProjectInput {
  name: string;
  client: string;
  description: string | null;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string | null;
}

export interface UpdateProjectInput {
  name?: string;
  client?: string;
  description?: string | null;
  startDate?: string;
  deadline?: string;
  priority?: ProjectPriority;
  supervisorId?: string | null;
  status?: ProjectStatus;
  health?: ProjectHealth;
  progress?: number;
}
