/**
 * Teams API module.
 */

import { TeamViewModel, WorkerViewModel } from '@/types';
import { apiClient } from './client';

export async function getTeams(): Promise<TeamViewModel[]> {
  return apiClient.get<TeamViewModel[]>('/teams');
}

export async function getTeamById(id: string): Promise<TeamViewModel | null> {
  return apiClient.get<TeamViewModel>(`/teams/${id}`);
}

export async function getTeamsBySupervisor(supervisorId: string): Promise<TeamViewModel[]> {
  return apiClient.get<TeamViewModel[]>('/teams', { supervisor_id: supervisorId });
}

export async function getTeamWorkers(teamId: string): Promise<WorkerViewModel[]> {
  return apiClient.get<WorkerViewModel[]>(`/teams/${teamId}/workers`);
}
