/**
 * Supervisors API module.
 *
 * In mock mode: reads from SupervisorsRepository.
 * In API mode: communicates with /api/v1/supervisors endpoints.
 */

import { Supervisor } from '@/types';
import { apiClient } from './client';
import { mockSupervisorsRepo } from './mock/supervisors-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getSupervisors(): Promise<Supervisor[]> {
  if (USE_MOCK) return mockSupervisorsRepo.getAll();
  return apiClient.get<Supervisor[]>('/supervisors');
}

export async function getSupervisorById(id: string): Promise<Supervisor | null> {
  if (USE_MOCK) return mockSupervisorsRepo.getById(id);
  return apiClient.get<Supervisor>(`/supervisors/${id}`);
}
