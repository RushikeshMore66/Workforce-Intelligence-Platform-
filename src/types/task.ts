import { ProjectPriority } from './project';

export type TaskStatus =
  | 'PLANNED'
  | 'IN_PROGRESS'
  | 'ON_HOLD'
  | 'COMPLETED'
  | 'CANCELLED';

export interface Task {
  id: string;
  projectId: string;
  title: string;
  description?: string;
  assigneeId: string | null;
  teamId: string | null;
  status: TaskStatus;
  priority: ProjectPriority;
  dueDate: string;
  createdAt: string;
  updatedAt?: string;
}

export interface CreateTaskInput {
  projectId: string;
  title: string;
  description?: string;
  assigneeId?: string;
  teamId?: string;
  priority: ProjectPriority;
  dueDate: string;
}

export interface UpdateTaskInput extends Partial<CreateTaskInput> {}

export interface ChangeTaskStatusInput {
  status: TaskStatus;
  reason?: string;
}
