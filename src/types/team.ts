export interface Team {
  id: string;
  name: string;
  supervisorId: string;
  teamLeaderId?: string;
}

export interface TeamMetrics {
  memberCount: number;
  projectIds: string[];
}

export type TeamViewModel = Team & TeamMetrics;
