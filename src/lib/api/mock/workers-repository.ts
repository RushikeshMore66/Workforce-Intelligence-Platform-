import { WorkerViewModel } from '@/types';
import { WORKERS } from '@/lib/mock-data/users';

function delay(ms = 250) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class WorkersRepository {
  async getAll(): Promise<WorkerViewModel[]> {
    await delay();
    return WORKERS;
  }

  async getById(id: string): Promise<WorkerViewModel | null> {
    await delay(150);
    return WORKERS.find(w => w.id === id) ?? null;
  }

  async getByTeam(teamId: string): Promise<WorkerViewModel[]> {
    await delay();
    return WORKERS.filter(w => w.teamId === teamId);
  }

  async getBySupervisor(supervisorId: string): Promise<WorkerViewModel[]> {
    await delay();
    return WORKERS.filter(w => w.supervisorId === supervisorId);
  }

  async getByProject(projectId: string): Promise<WorkerViewModel[]> {
    await delay();
    return WORKERS.filter(w => w.activeProjectId === projectId);
  }
}

export const mockWorkersRepo = new WorkersRepository();
