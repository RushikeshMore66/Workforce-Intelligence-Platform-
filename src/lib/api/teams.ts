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

export async function getTeamWorkers(teamId: string): Promise<unknown[]> {
  if (USE_MOCK) return []; // Covered by workers mock
  return apiClient.get<unknown[]>(`/teams/${teamId}/workers`);
}

/**
 * @deprecated Backend endpoint NOT AVAILABLE yet.
 */
export async function getTeamLeaderById(id: string): Promise<TeamLeader | null> {
  if (USE_MOCK) return mockTeamsRepo.getLeaderById(id);
  throw new Error('Not implemented in backend');
}

/**
 * @deprecated Backend endpoint NOT AVAILABLE yet.
 */
export async function getAllTeamLeaders(): Promise<TeamLeader[]> {
  if (USE_MOCK) return mockTeamsRepo.getAllLeaders();
  throw new Error('Not implemented in backend');
}
