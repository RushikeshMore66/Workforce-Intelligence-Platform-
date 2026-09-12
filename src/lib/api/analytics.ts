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

export async function getOrganizationAnalytics(): Promise<OrganizationAnalyticsResponse> {
  return apiClient.get<OrganizationAnalyticsResponse>('/analytics/organization');
}

export async function getProjectAnalytics(projectId: string): Promise<ProjectAnalyticsResponse> {
  return apiClient.get<ProjectAnalyticsResponse>(`/projects/${projectId}/analytics`);
}

export async function getTeamAnalytics(teamId: string): Promise<TeamAnalyticsResponse> {
  return apiClient.get<TeamAnalyticsResponse>(`/teams/${teamId}/analytics`);
}

export async function getWorkerAnalytics(workerId: string): Promise<WorkerAnalyticsResponse> {
  return apiClient.get<WorkerAnalyticsResponse>(`/workers/${workerId}/analytics`);
}
