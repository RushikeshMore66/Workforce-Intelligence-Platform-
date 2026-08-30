import { Worker } from '@/types';
import { mockWorkersRepo } from './mock/workers-repository';

export async function getWorkers(): Promise<Worker[]> {
  return mockWorkersRepo.getAll();
}

export async function getWorkerById(id: string): Promise<Worker | null> {
  return mockWorkersRepo.getById(id);
}

export async function getWorkersByTeam(teamId: string): Promise<Worker[]> {
  return mockWorkersRepo.getByTeam(teamId);
}

export async function getWorkersBySupervisor(supervisorId: string): Promise<Worker[]> {
  return mockWorkersRepo.getBySupervisor(supervisorId);
}

export async function getWorkersByProject(projectId: string): Promise<Worker[]> {
  return mockWorkersRepo.getByProject(projectId);
}
