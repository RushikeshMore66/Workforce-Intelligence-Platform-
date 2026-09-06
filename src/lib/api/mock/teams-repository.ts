import { TeamViewModel, TeamLeader } from '@/types';
import { TEAMS, TEAM_LEADERS } from '@/lib/mock-data/users';

function delay(ms = 250) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class TeamsRepository {
  async getAll(): Promise<TeamViewModel[]> {
    await delay();
    return TEAMS;
  }

  async getById(id: string): Promise<TeamViewModel | null> {
    await delay(150);
    return TEAMS.find(t => t.id === id) ?? null;
  }

  async getBySupervisor(supervisorId: string): Promise<TeamViewModel[]> {
    await delay();
    return TEAMS.filter(t => t.supervisorId === supervisorId);
  }

  async getLeaderById(id: string): Promise<TeamLeader | null> {
    await delay(150);
    return TEAM_LEADERS.find(tl => tl.id === id) ?? null;
  }

  async getAllLeaders(): Promise<TeamLeader[]> {
    await delay();
    return TEAM_LEADERS;
  }
}

export const mockTeamsRepo = new TeamsRepository();
