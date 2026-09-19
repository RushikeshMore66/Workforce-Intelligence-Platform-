/**
 * Supervisors API module.
 */

import { Supervisor } from '@/types';
import { apiClient } from './client';

export async function getSupervisors(): Promise<Supervisor[]> {
  return apiClient.get<Supervisor[]>('/supervisors');
}

export async function getSupervisorById(id: string): Promise<Supervisor | null> {
  return apiClient.get<Supervisor>(`/supervisors/${id}`);
}
