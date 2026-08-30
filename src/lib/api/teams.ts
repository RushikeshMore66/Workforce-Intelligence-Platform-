import { Team, TeamLeader } from '@/types';
import { mockTeamsRepo } from './mock/teams-repository';

export async function getTeams(): Promise<Team[]> {
  return mockTeamsRepo.getAll();
}

export async function getTeamById(id: string): Promise<Team | null> {
  return mockTeamsRepo.getById(id);
}

export async function getTeamsBySupervisor(supervisorId: string): Promise<Team[]> {
  return mockTeamsRepo.getBySupervisor(supervisorId);
}

export async function getTeamLeaderById(id: string): Promise<TeamLeader | null> {
  return mockTeamsRepo.getLeaderById(id);
}

export async function getAllTeamLeaders(): Promise<TeamLeader[]> {
  return mockTeamsRepo.getAllLeaders();
}
