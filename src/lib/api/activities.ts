/**
 * Activities API module.
 * Queries for ProjectActivity audit events.
 *
 * In mock mode: reads from PROJECT_ACTIVITIES static data.
 * In API mode: communicates with /api/v1/activities endpoints.
 */

import { ProjectActivity } from '@/types';
import { apiClient } from './client';
import { PROJECT_ACTIVITIES } from '@/lib/mock-data/activities';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

function delay(ms = 200) {
  return new Promise(r => setTimeout(r, ms));
}

export async function getRecentActivities(limit = 10): Promise<ProjectActivity[]> {
  if (USE_MOCK) {
    await delay();
    return PROJECT_ACTIVITIES.slice(0, limit);
  }
  return apiClient.get<ProjectActivity[]>('/dashboard/activities', { limit });
}

export async function getActivitiesByProject(projectId: string): Promise<ProjectActivity[]> {
  if (USE_MOCK) {
    await delay();
    return PROJECT_ACTIVITIES.filter(a => a.projectId === projectId);
  }
  return apiClient.get<ProjectActivity[]>(`/projects/${projectId}/activities`);
}

/**
 * @deprecated Backend endpoint GET /activities?user_id=X is NOT AVAILABLE yet.
 */
export async function getActivitiesByUser(userId: string): Promise<ProjectActivity[]> {
  if (USE_MOCK) {
    await delay();
    return PROJECT_ACTIVITIES.filter(a => a.userId === userId);
  }
  throw new Error('Not implemented in backend');
}
