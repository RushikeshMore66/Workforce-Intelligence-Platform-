/**
 * Tasks API module.
 *
 * Task metadata and task status transitions are intentionally separate:
 * - updateTask() edits metadata (management only on the backend)
 * - changeTaskStatus() executes a validated workflow transition
 */

import {
  Task,
  ChangeTaskStatusInput,
  CreateTaskInput,
  UpdateTaskInput,
} from '@/types';
import { apiClient } from './client';
import { TASKS } from '@/lib/mock-data/tasks';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

function delay(ms = 200) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getTasks(): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS;
  }

  throw new Error(
    'GET /tasks is not implemented in backend. Fetch tasks by project.'
  );
}

export async function getTaskById(id: string): Promise<Task | null> {
  if (USE_MOCK) {
    await delay();
    return TASKS.find((task) => task.id === id) ?? null;
  }

  return apiClient.get<Task>(`/tasks/${id}`);
}

export async function getTasksByProject(projectId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter((task) => task.projectId === projectId);
  }

  return apiClient.get<Task[]>(`/projects/${projectId}/tasks`);
}

export async function getTasksByWorker(workerId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter((task) => task.assigneeId === workerId);
  }

  return apiClient.get<Task[]>('/tasks', { assignee_id: workerId });
}

export async function getTasksByTeam(teamId: string): Promise<Task[]> {
  if (USE_MOCK) {
    await delay();
    return TASKS.filter((task) => task.teamId === teamId);
  }

  return apiClient.get<Task[]>('/tasks', { team_id: teamId });
}

export async function createTask(input: CreateTaskInput): Promise<Task> {
  if (USE_MOCK) {
    await delay(400);

    const task: Task = {
      ...input,
      id: `t-${Date.now()}`,
      status: 'PLANNED',
      assigneeId: input.assigneeId ?? null,
      teamId: input.teamId ?? null,
      createdAt: new Date().toISOString(),
    };

    return task;
  }

  return apiClient.post<Task>('/tasks', input);
}

export async function updateTask(
  id: string,
  input: UpdateTaskInput,
): Promise<Task | null> {
  if (USE_MOCK) {
    await delay(300);

    const task = TASKS.find((item) => item.id === id);
    if (!task) return null;

    return { ...task, ...input };
  }

  return apiClient.patch<Task>(`/tasks/${id}`, input);
}

export async function changeTaskStatus(
  id: string,
  input: ChangeTaskStatusInput,
): Promise<Task> {
  if (USE_MOCK) {
    await delay(250);

    const task = TASKS.find((item) => item.id === id);
    if (!task) {
      throw new Error('Task not found');
    }

    task.status = input.status;
    return { ...task };
  }

  return apiClient.post<Task>(`/tasks/${id}/status`, input);
}

export async function deleteTask(id: string): Promise<boolean> {
  if (USE_MOCK) {
    await delay(300);
    return TASKS.some((task) => task.id === id);
  }

  await apiClient.delete(`/tasks/${id}`);
  return true;
}
