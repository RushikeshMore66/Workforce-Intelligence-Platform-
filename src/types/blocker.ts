export type BlockerStatus = 'OPEN' | 'RESOLVED';

export interface Blocker {
  id: string;
  projectId: string;
  taskId?: string | null;
  title: string;
  description: string;
  reportedById: string | null;
  teamId: string | null;
  createdDate: string;
  resolvedDate?: string | null;
  status: BlockerStatus;
}

export interface CreateBlockerInput {
  projectId: string;
  taskId?: string;
  title: string;
  description: string;
  teamId?: string;
}
