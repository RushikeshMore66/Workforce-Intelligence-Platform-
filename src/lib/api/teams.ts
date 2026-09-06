/**
 * Teams API module.
 *
 * In mock mode: reads from TeamsRepository.
 * In API mode: communicates with /api/v1/teams endpoints.
 */

import { TeamViewModel, TeamLeader } from '@/types';
import { apiClient } from './client';
import { mockTeamsRepo } from './mock/teams-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getTeams(): Promise<TeamViewModel[]> {
  if (USE_MOCK) return mockTeamsRepo.getAll();
  return apiClient.get<TeamViewModel[]>('/teams');
}

export async function getTeamById(id: string): Promise<TeamViewModel | null> {
  if (USE_MOCK) return mockTeamsRepo.getById(id);
  return apiClient.get<TeamViewModel>(`/teams/${id}`);
}

export async function getTeamsBySupervisor(supervisorId: string): Promise<TeamViewModel[]> {
  if (USE_MOCK) return mockTeamsRepo.getBySupervisor(supervisorId);
  return apiClient.get<TeamViewModel[]>(`/teams?supervisor_id=${supervisorId}`);
}

export async function getTeamLeaderById(id: string): Promise<TeamLeader | null> {
  if (USE_MOCK) return mockTeamsRepo.getLeaderById(id);
  return apiClient.get<TeamLeader>(`/team-leaders/${id}`);
}

export async function getAllTeamLeaders(): Promise<TeamLeader[]> {
  if (USE_MOCK) return mockTeamsRepo.getAllLeaders();
  return apiClient.get<TeamLeader[]>('/team-leaders');
}
