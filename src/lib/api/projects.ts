/**
 * Projects API module.
 * CRUD operations and queries for Project entities.
 *
 * In mock mode: reads/writes from localStorage-backed ProjectsRepository.
 * In API mode: communicates with /api/v1/projects endpoints.
 */

import { CreateProjectInput, ProjectViewModel, UpdateProjectInput, ProjectDetail } from '@/types';
import { apiClient } from './client';
import { mockProjectsRepo } from './mock/projects-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export interface ProjectFilters {
  search?: string;
  status?: string;
  health?: string;
  priority?: string;
}

export async function getProjects(filters?: ProjectFilters): Promise<ProjectViewModel[]> {
  if (USE_MOCK) return mockProjectsRepo.getAll();
  return apiClient.get<ProjectViewModel[]>('/projects', filters as Record<string, string | undefined>);
}

export async function getProjectById(id: string): Promise<ProjectDetail | null> {
  if (USE_MOCK) {
    const p = await mockProjectsRepo.getById(id);
    return p ? { ...p, teamIds: [] } : null;
  }
  return apiClient.get<ProjectDetail>(`/projects/${id}`);
}

export async function createProject(input: CreateProjectInput): Promise<ProjectViewModel> {
  if (USE_MOCK) return mockProjectsRepo.create(input);
  return apiClient.post<ProjectViewModel>('/projects', input);
}

export async function updateProject(id: string, input: UpdateProjectInput): Promise<ProjectViewModel | null> {
  if (USE_MOCK) return mockProjectsRepo.update(id, input);
  return apiClient.patch<ProjectViewModel>(`/projects/${id}`, input);
}

export async function deleteProject(id: string): Promise<boolean> {
  if (USE_MOCK) return mockProjectsRepo.delete(id);
  await apiClient.delete(`/projects/${id}`);
  return true;
}
