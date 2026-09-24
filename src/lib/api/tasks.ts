/**
 * Tasks API module.
 * CRUD operations and queries for Task entities.
 */

import { Task, CreateTaskInput, UpdateTaskInput } from '@/types';
import { apiClient } from './client';

/**
 * @deprecated Backend endpoint GET /tasks is NOT AVAILABLE. Use getTasksByProject instead.
 */
export async function getTasks(): Promise<Task[]> {
  throw new Error('GET /tasks is not implemented in backend. Fetch tasks by project.');
}

export async function getTaskById(id: string): Promise<Task | null> {
  return apiClient.get<Task>(`/tasks/${id}`);
}

export async function getTasksByProject(projectId: string): Promise<Task[]> {
  return apiClient.get<Task[]>(`/projects/${projectId}/tasks`);
}

/**
 * Note: Uses generic task filtering if added to backend, otherwise fails in prod.
 */
export async function getTasksByWorker(workerId: string): Promise<Task[]> {
  // This assumes the backend adds support for /tasks?assignee_id=X eventually,
  // currently we know only GET /projects/:id/tasks is fully implemented.
  return apiClient.get<Task[]>('/tasks', { assignee_id: workerId });
}

/**
 * Note: Uses generic task filtering if added to backend, otherwise fails in prod.
 */
export async function getTasksByTeam(teamId: string): Promise<Task[]> {
  return apiClient.get<Task[]>('/tasks', { team_id: teamId });
}

export async function createTask(input: CreateTaskInput): Promise<Task> {
  return apiClient.post<Task>('/tasks', input);
}

export async function updateTask(id: string, input: UpdateTaskInput): Promise<Task | null> {
  return apiClient.patch<Task>(`/tasks/${id}`, input);
}

export async function deleteTask(id: string): Promise<boolean> {
  await apiClient.delete(`/tasks/${id}`);
  return true;
}
