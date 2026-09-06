export type ProjectStatus = 'PLANNED' | 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED';
export type ProjectHealth = 'ON_TRACK' | 'AT_RISK' | 'DELAYED';
export type ProjectPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export interface Project {
  id: string;
  name: string;
  client: string;
  description: string;
  startDate: string;
  deadline: string;
  priority: ProjectPriority;
  supervisorId: string | null;
  status: ProjectStatus;
  health: ProjectHealth;
  progress: number;
  createdAt: string;
  updatedAt?: string;
}

export interface ProjectMetrics {
  teamCount: number;
}

export type ProjectViewModel = Project & ProjectMetrics;

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
