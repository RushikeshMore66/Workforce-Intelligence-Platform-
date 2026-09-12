export interface WorkforceMetrics {
  totalWorkers?: number;
  activeWorkers?: number;
  workersWithTasks?: number;
  workersWithoutTasks?: number;
  totalTeams?: number;
  activeTeams?: number;
  totalProjects?: number;
  activeProjects?: number;
  teamWorkforceCount?: number;
}

export interface WorkloadMetrics {
  total?: number;
  totalTasks?: number;
  todo: number;
  inProgress: number;
  blocked: number;
  completed: number;
  overdue: number;
  unassigned: number;
}

export interface ActivityMetrics {
  totalUpdates: number;
  updatesLast7Days: number;
  updatesLast30Days: number;
  lastUpdateAt: string | null;
  workerAuthoredUpdates: number;
  managementAuthoredUpdates: number;
}

export interface DeliveryMetrics {
  completedTasks: number;
  completionRate: number;
  averageCycleTime: number | null; // in hours
  tasksWithValidTransitionHistory: number;
  tasksMissingTransitionHistory: number;
}

export interface AttentionMetrics {
  overdueTasks: number;
  blockedTasks: number;
  unassignedTasks: number;
  atRiskProjects: number;
  workersWithNoRecentActivity: number;
}

export interface OrganizationAnalyticsResponse {
  workforce: WorkforceMetrics;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
  attention: AttentionMetrics;
}

export interface ProjectAnalyticsResponse {
  workforce: WorkforceMetrics;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}

export interface TeamAnalyticsResponse {
  workforce: WorkforceMetrics;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}

export interface WorkerAnalyticsResponse {
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}
