/**
 * Projects API module.
 *
 * Project metadata updates and project lifecycle transitions are separate
 * operations so the UI cannot accidentally bypass workflow rules.
 */

import {
  ChangeProjectStatusInput,
  CreateProjectInput,
  ProjectDetail,
  ProjectViewModel,
  UpdateProjectInput,
} from '@/types';
import { apiClient } from './client';

export interface ProjectFilters {
  search?: string;
  status?: string;
  health?: string;
  priority?: string;
}

export async function getProjects(
  filters?: ProjectFilters,
): Promise<ProjectViewModel[]> {
  return apiClient.get<ProjectViewModel[]>(
    '/projects',
    filters as Record<string, string | undefined>,
  );
}

export async function getProjectById(
  id: string,
): Promise<ProjectDetail | null> {
  return apiClient.get<ProjectDetail>(`/projects/${id}`);
}

export async function createProject(
  input: CreateProjectInput,
): Promise<ProjectViewModel> {
  return apiClient.post<ProjectViewModel>('/projects', input);
}

export async function updateProject(
  id: string,
  input: UpdateProjectInput,
): Promise<ProjectViewModel | null> {
  return apiClient.patch<ProjectViewModel>(`/projects/${id}`, input);
}

export async function changeProjectStatus(
  id: string,
  input: ChangeProjectStatusInput,
): Promise<ProjectViewModel> {
  return apiClient.post<ProjectViewModel>(
    `/projects/${id}/status`,
    input,
  );
}

export async function deleteProject(id: string): Promise<boolean> {
  await apiClient.delete(`/projects/${id}`);
  return true;
}
