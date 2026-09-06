/**
 * Tasks API module.
 * CRUD operations and queries for Task entities.
 *
 * In mock mode: reads from TASKS static data.
 * In API mode: communicates with /api/v1/tasks endpoints.
 */

import { Task, CreateTaskInput, UpdateTaskInput } from '@/types';
import { apiClient } from './client';
import { TASKS } from '@/lib/mock-data/tasks';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

function delay(ms = 200) {
  return new Promise(r => setTimeout(r, ms));
}

export async function getTasks(): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS;
  }
  return apiClient.get<Task[]>('/tasks');
}

export async function getTaskById(id: string): Promise<Task | null> {
  if (USE_MOCK) {
    await delay();
    return TASKS.find(t => t.id === id) ?? null;
  }
  return apiClient.get<Task>(`/tasks/${id}`);
}

export async function getTasksByProject(projectId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter(t => t.projectId === projectId);
  }
  return apiClient.get<Task[]>(`/projects/${projectId}/tasks`);
}

export async function getTasksByWorker(workerId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter(t => t.assigneeId === workerId);
  }
  return apiClient.get<Task[]>(`/tasks?assignee_id=${workerId}`);
}

export async function getTasksByTeam(teamId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter(t => t.teamId === teamId);
  }
  return apiClient.get<Task[]>(`/tasks?team_id=${teamId}`);
}

export async function createTask(input: CreateTaskInput): Promise<Task> {
  if (USE_MOCK) {
    await delay(400);
    const task: Task = {
      ...input,
      id: `t-${Date.now()}`,
      status: 'TODO',
      assigneeId: input.assigneeId ?? null,
      teamId: input.teamId ?? null,
      createdAt: new Date().toISOString(),
    };
    return task;
  }
  return apiClient.post<Task>('/tasks', input);
}

export async function updateTask(id: string, input: UpdateTaskInput): Promise<Task | null> {
  if (USE_MOCK) {
    await delay(300);
    const task = TASKS.find(t => t.id === id);
    if (!task) return null;
    return { ...task, ...input };
  }
  return apiClient.patch<Task>(`/tasks/${id}`, input);
}

export async function deleteTask(id: string): Promise<boolean> {
  if (USE_MOCK) {
    await delay(300);
    return TASKS.some(t => t.id === id);
  }
  await apiClient.delete(`/tasks/${id}`);
  return true;
}
