/**
 * Workers API module.
 *
 * In mock mode: reads from WorkersRepository.
 * In API mode: communicates with /api/v1/workers endpoints.
 */

import { Worker } from '@/types';
import { apiClient } from './client';
import { mockWorkersRepo } from './mock/workers-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getWorkers(): Promise<Worker[]> {
  if (USE_MOCK) return mockWorkersRepo.getAll();
  return apiClient.get<Worker[]>('/workers');
}

export async function getWorkerById(id: string): Promise<Worker | null> {
  if (USE_MOCK) return mockWorkersRepo.getById(id);
  return apiClient.get<Worker>(`/workers/${id}`);
}

export async function getWorkersByTeam(teamId: string): Promise<Worker[]> {
  if (USE_MOCK) return mockWorkersRepo.getByTeam(teamId);
  return apiClient.get<Worker[]>(`/workers?team_id=${teamId}`);
}

export async function getWorkersBySupervisor(supervisorId: string): Promise<Worker[]> {
  if (USE_MOCK) return mockWorkersRepo.getBySupervisor(supervisorId);
  return apiClient.get<Worker[]>(`/workers?supervisor_id=${supervisorId}`);
}

export async function getWorkersByProject(projectId: string): Promise<Worker[]> {
  if (USE_MOCK) return mockWorkersRepo.getByProject(projectId);
  return apiClient.get<Worker[]>(`/workers?project_id=${projectId}`);
}
