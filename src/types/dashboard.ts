export interface AttentionItem {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
  projectId?: string;
  type: 'RISK' | 'DEADLINE' | 'BLOCKER' | 'OVERLOAD' | 'REVIEW';
}

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
