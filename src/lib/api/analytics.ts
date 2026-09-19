/**
 * Analytics API module.
 */

import {
  OrganizationAnalyticsResponse,
  ProjectAnalyticsResponse,
  TeamAnalyticsResponse,
  WorkerAnalyticsResponse,
} from '@/types/analytics';
import { apiClient } from './client';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

const MOCK_ORG_ANALYTICS: OrganizationAnalyticsResponse = {
  workforce: {
    totalWorkers: 70,
    activeWorkers: 61,
    workersWithTasks: 50,
    workersWithoutTasks: 20,
    totalTeams: 6,
    activeTeams: 6,
    totalProjects: 12,
    activeProjects: 12,
  },
  workload: {
    todo: 45,
    inProgress: 24,
    blocked: 8,
    completed: 284,
    overdue: 3,
    unassigned: 5,
  },
  activity: {
    totalUpdates: 1024,
    updatesLast7Days: 45,
    updatesLast30Days: 120,
    lastUpdateAt: new Date().toISOString(),
    workerAuthoredUpdates: 800,
    managementAuthoredUpdates: 224,
  },
  delivery: {
    completedTasks: 284,
    completionRate: 0.85,
    averageCycleTime: 42.5,
    tasksWithValidTransitionHistory: 300,
    tasksMissingTransitionHistory: 10,
  },
  attention: {
    overdueTasks: 3,
    blockedTasks: 8,
    unassignedTasks: 5,
    atRiskProjects: 3,
    workersWithNoRecentActivity: 2,
  }
};

export async function getOrganizationAnalytics(): Promise<OrganizationAnalyticsResponse> {
  if (USE_MOCK) return MOCK_ORG_ANALYTICS;
  return apiClient.get<OrganizationAnalyticsResponse>('/analytics/organization');
}

export async function getProjectAnalytics(projectId: string): Promise<ProjectAnalyticsResponse> {
  if (USE_MOCK) {
    return {
      workforce: MOCK_ORG_ANALYTICS.workforce,
      workload: MOCK_ORG_ANALYTICS.workload,
      activity: MOCK_ORG_ANALYTICS.activity,
      delivery: MOCK_ORG_ANALYTICS.delivery,
    };
  }
  return apiClient.get<ProjectAnalyticsResponse>(`/projects/${projectId}/analytics`);
}

export async function getTeamAnalytics(teamId: string): Promise<TeamAnalyticsResponse> {
  if (USE_MOCK) {
    return {
      workforce: MOCK_ORG_ANALYTICS.workforce,
      workload: MOCK_ORG_ANALYTICS.workload,
      activity: MOCK_ORG_ANALYTICS.activity,
      delivery: MOCK_ORG_ANALYTICS.delivery,
    };
  }
  return apiClient.get<TeamAnalyticsResponse>(`/teams/${teamId}/analytics`);
}

export async function getWorkerAnalytics(workerId: string): Promise<WorkerAnalyticsResponse> {
  if (USE_MOCK) {
    return {
      workload: MOCK_ORG_ANALYTICS.workload,
      activity: MOCK_ORG_ANALYTICS.activity,
      delivery: MOCK_ORG_ANALYTICS.delivery,
    };
  }
  return apiClient.get<WorkerAnalyticsResponse>(`/workers/${workerId}/analytics`);
}
