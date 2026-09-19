/**
 * Blockers API module.
 * CRUD operations and queries for Blocker entities.
 */

import { Blocker, CreateBlockerInput } from '@/types';
import { apiClient } from './client';

export async function getBlockers(): Promise<Blocker[]> {
  return apiClient.get<Blocker[]>('/blockers');
}

export async function getBlockerById(id: string): Promise<Blocker | null> {
  return apiClient.get<Blocker>(`/blockers/${id}`);
}

export async function getBlockersByProject(projectId: string): Promise<Blocker[]> {
  return apiClient.get<Blocker[]>(`/projects/${projectId}/blockers`);
}

export async function getBlockersByTeam(teamId: string): Promise<Blocker[]> {
  return apiClient.get<Blocker[]>('/blockers', { team_id: teamId });
}

export async function getOpenBlockers(): Promise<Blocker[]> {
  return apiClient.get<Blocker[]>('/blockers', { status: 'OPEN' });
}

export async function createBlocker(input: CreateBlockerInput): Promise<Blocker> {
  return apiClient.post<Blocker>('/blockers', input);
}

export async function updateBlocker(id: string, input: Partial<CreateBlockerInput> & { status?: 'OPEN' | 'RESOLVED' }): Promise<Blocker | null> {
  return apiClient.patch<Blocker>(`/blockers/${id}`, input);
}

export async function resolveBlocker(id: string): Promise<Blocker | null> {
  return apiClient.patch<Blocker>(`/blockers/${id}`, { status: 'RESOLVED' });
}
