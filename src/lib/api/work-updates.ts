/**
 * Work Updates API module.
 * CRUD operations for WorkUpdate entities.
 *
 * In mock mode: returns empty arrays (work updates not in static mock data yet).
 * In API mode: communicates with /api/v1/work-updates endpoints.
 */

import { WorkUpdate, CreateWorkUpdateInput } from '@/types';
import { apiClient } from './client';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

function delay(ms = 200) {
  return new Promise(r => setTimeout(r, ms));
}

/**
 * @deprecated Backend GET /tasks/:id/updates is NOT AVAILABLE yet.
 */
export async function getWorkUpdatesByTask(_taskId: string): Promise<WorkUpdate[]> {
  if (USE_MOCK) {
    await delay();
    return []; // Work updates not yet in mock data
  }
  throw new Error('GET /tasks/:id/updates is not implemented in backend');
}

/**
 * @deprecated Backend GET /work-updates is NOT AVAILABLE yet.
 */
export async function getWorkUpdatesByWorker(_workerId: string): Promise<WorkUpdate[]> {
  if (USE_MOCK) {
    await delay();
    return [];
  }
  throw new Error('GET /work-updates is not implemented in backend');
}

export async function createWorkUpdate(input: CreateWorkUpdateInput): Promise<WorkUpdate> {
  if (USE_MOCK) {
    await delay(400);
    const update: WorkUpdate = {
      id: `wu-${Date.now()}`,
      taskId: input.taskId,
      workerId: 'mock-worker',
      description: input.description,
      timestamp: new Date().toISOString(),
    };
    return update;
  }
  return apiClient.post<WorkUpdate>(`/tasks/${input.taskId}/updates`, input);
}
