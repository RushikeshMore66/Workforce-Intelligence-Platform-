/**
 * Activities API module.
 * Queries for ProjectActivity audit events.
 */

import { ProjectActivity } from '@/types';
import { apiClient } from './client';

export async function getRecentActivities(limit = 10): Promise<ProjectActivity[]> {
  return apiClient.get<ProjectActivity[]>('/dashboard/activities', { limit });
}

export async function getActivitiesByProject(projectId: string): Promise<ProjectActivity[]> {
  return apiClient.get<ProjectActivity[]>(`/projects/${projectId}/activities`);
}
