/**
 * Analytics TypeScript types — aligned to backend API contract.
 *
 * Field names here must match the camelCase-converted backend schema fields.
 * The API client (toCamelCase) converts snake_case → camelCase, so:
 *   planned      → planned
 *   on_hold      → onHold
 *   average_cycle_time_hours → averageCycleTimeHours
 *   on_hold_tasks → onHoldTasks
 */

export interface WorkforceMetrics {
  totalWorkers?: number;
  activeWorkers?: number;
  workersWithTasks?: number;
  workersWithoutTasks?: number;
  workersWithOverdueTasks?: number;
  totalTeams?: number;
  activeTeams?: number;
  totalProjects?: number;
  activeProjects?: number;
  teamWorkforceCount?: number;
}

/** Workload breakdown — field names match backend camelCase conversion */
export interface WorkloadMetrics {
  total?: number;
  /** PLANNED tasks */
  planned: number;
  inProgress: number;
  /** ON_HOLD tasks (awaiting something) */
  onHold: number;
  completed: number;
  cancelled?: number;
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
  /** Average cycle time in hours — field name matches backend average_cycle_time_hours */
  averageCycleTimeHours: number | null;
  /** Alias present for backwards compatibility in some views */
  averageCycleTime?: number | null;
  tasksWithValidTransitionHistory: number;
  tasksMissingTransitionHistory: number;
}

export interface AttentionMetrics {
  overdueTasks: number;
  /** ON_HOLD tasks requiring attention */
  onHoldTasks: number;
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
  projectId: string;
  workforce: WorkforceMetrics;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}

export interface TeamAnalyticsResponse {
  teamId: string;
  workforce: WorkforceMetrics;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}

export interface WorkerAnalyticsResponse {
  workerId: string;
  workload: WorkloadMetrics;
  activity: ActivityMetrics;
  delivery: DeliveryMetrics;
}
