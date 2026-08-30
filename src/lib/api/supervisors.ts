import { Supervisor } from '@/types';
import { mockSupervisorsRepo } from './mock/supervisors-repository';

export async function getSupervisors(): Promise<Supervisor[]> {
  return mockSupervisorsRepo.getAll();
}

export async function getSupervisorById(id: string): Promise<Supervisor | null> {
  return mockSupervisorsRepo.getById(id);
}
