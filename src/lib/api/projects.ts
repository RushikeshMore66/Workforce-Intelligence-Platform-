/**
 * Projects API module.
 * CRUD operations and queries for Project entities.
 *
 * In mock mode: reads/writes from localStorage-backed ProjectsRepository.
 * In API mode: communicates with /api/v1/projects endpoints.
 */

import { CreateProjectInput, Project, UpdateProjectInput } from '@/types';
import { apiClient } from './client';
import { mockProjectsRepo } from './mock/projects-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getProjects(): Promise<Project[]> {
  if (USE_MOCK) return mockProjectsRepo.getAll();
  return apiClient.get<Project[]>('/projects');
}

export async function getProjectById(id: string): Promise<Project | null> {
  if (USE_MOCK) return mockProjectsRepo.getById(id);
  return apiClient.get<Project>(`/projects/${id}`);
}

export async function createProject(input: CreateProjectInput): Promise<Project> {
  if (USE_MOCK) return mockProjectsRepo.create(input);
  return apiClient.post<Project>('/projects', input);
}

export async function updateProject(id: string, input: UpdateProjectInput): Promise<Project | null> {
  if (USE_MOCK) return mockProjectsRepo.update(id, input);
  return apiClient.patch<Project>(`/projects/${id}`, input);
}

export async function deleteProject(id: string): Promise<boolean> {
  if (USE_MOCK) return mockProjectsRepo.delete(id);
  await apiClient.delete(`/projects/${id}`);
  return true;
}
