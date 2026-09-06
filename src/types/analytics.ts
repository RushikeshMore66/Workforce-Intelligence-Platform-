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
