export interface WorkUpdate {
  id: string;
  taskId: string;
  workerId: string;
  description: string;
  progress?: number;
  timestamp: string;
}

export interface CreateWorkUpdateInput {
  taskId: string;
  description: string;
  progress?: number;
}
