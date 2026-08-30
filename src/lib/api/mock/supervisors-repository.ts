import { Supervisor } from '@/types';
import { SUPERVISORS } from '@/lib/mock-data/users';

function delay(ms = 250) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class SupervisorsRepository {
  async getAll(): Promise<Supervisor[]> {
    await delay();
    return SUPERVISORS;
  }

  async getById(id: string): Promise<Supervisor | null> {
    await delay(150);
    return SUPERVISORS.find(s => s.id === id) ?? null;
  }
}

export const mockSupervisorsRepo = new SupervisorsRepository();
