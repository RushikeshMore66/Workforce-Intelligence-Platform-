/**
 * Workers API module.
 */

import { WorkerViewModel } from '@/types';
import { apiClient } from './client';

export interface GetWorkersParams {
  search?: string;
  team_id?: string;
  status?: string;
}

export async function getWorkers(params?: GetWorkersParams): Promise<WorkerViewModel[]> {
  return apiClient.get<WorkerViewModel[]>('/workers', params as Record<string, string | undefined>);
}

export async function getWorkerById(id: string): Promise<WorkerViewModel | null> {
  return apiClient.get<WorkerViewModel>(`/workers/${id}`);
}

export async function getWorkersByTeam(teamId: string): Promise<WorkerViewModel[]> {
  return apiClient.get<WorkerViewModel[]>('/workers', { team_id: teamId });
}

export async function getWorkersBySupervisor(supervisorId: string): Promise<WorkerViewModel[]> {
  return apiClient.get<WorkerViewModel[]>('/workers', { supervisor_id: supervisorId });
}

export async function getWorkersByProject(projectId: string): Promise<WorkerViewModel[]> {
  return apiClient.get<WorkerViewModel[]>('/workers', { project_id: projectId });
}
