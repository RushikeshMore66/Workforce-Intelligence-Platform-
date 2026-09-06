/**
 * Blockers API module.
 * CRUD operations and queries for Blocker entities.
 *
 * In mock mode: reads from BLOCKERS static data.
 * In API mode: communicates with /api/v1/blockers endpoints.
 */

import { Blocker, CreateBlockerInput } from '@/types';
import { apiClient } from './client';
import { BLOCKERS } from '@/lib/mock-data/blockers';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

function delay(ms = 200) {
  return new Promise(r => setTimeout(r, ms));
}

export async function getBlockers(): Promise<Blocker[]> {
  if (USE_MOCK) {
    await delay();
    return BLOCKERS;
  }
  return apiClient.get<Blocker[]>('/blockers');
}

export async function getBlockerById(id: string): Promise<Blocker | null> {
  if (USE_MOCK) {
    await delay();
    return BLOCKERS.find(b => b.id === id) ?? null;
  }
  return apiClient.get<Blocker>(`/blockers/${id}`);
}

export async function getBlockersByProject(projectId: string): Promise<Blocker[]> {
  if (USE_MOCK) {
    await delay();
    return BLOCKERS.filter(b => b.projectId === projectId);
  }
  return apiClient.get<Blocker[]>(`/projects/${projectId}/blockers`);
}

export async function getBlockersByTeam(teamId: string): Promise<Blocker[]> {
  if (USE_MOCK) {
    await delay();
    return BLOCKERS.filter(b => b.teamId === teamId);
  }
  return apiClient.get<Blocker[]>(`/blockers?team_id=${teamId}`);
}

export async function getOpenBlockers(): Promise<Blocker[]> {
  if (USE_MOCK) {
    await delay();
    return BLOCKERS.filter(b => b.status === 'OPEN');
  }
  return apiClient.get<Blocker[]>('/blockers?status=OPEN');
}

export async function createBlocker(input: CreateBlockerInput): Promise<Blocker> {
  if (USE_MOCK) {
    await delay(400);
    const blocker: Blocker = {
      ...input,
      id: `bl-${Date.now()}`,
      reportedById: null,
      teamId: input.teamId ?? null,
      createdDate: new Date().toISOString().split('T')[0],
      status: 'OPEN',
    };
    return blocker;
  }
  return apiClient.post<Blocker>('/blockers', input);
}

export async function resolveBlocker(id: string): Promise<Blocker | null> {
  if (USE_MOCK) {
    await delay(300);
    const blocker = BLOCKERS.find(b => b.id === id);
    if (!blocker) return null;
    return {
      ...blocker,
      status: 'RESOLVED',
      resolvedDate: new Date().toISOString().split('T')[0],
    };
  }
  return apiClient.patch<Blocker>(`/blockers/${id}/resolve`, {});
}
