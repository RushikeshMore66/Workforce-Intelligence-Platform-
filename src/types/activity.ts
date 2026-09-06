export type ActivityType =
  | 'PROJECT_CREATED'
  | 'PROJECT_UPDATED'
  | 'PROJECT_STATUS_CHANGED'
  | 'PROJECT_ASSIGNED'
  | 'TASK_CREATED'
  | 'TASK_UPDATED'
  | 'TASK_ASSIGNED'
  | 'TASK_STATUS_CHANGED'
  | 'TASK_COMPLETED'
  | 'WORK_UPDATE_ADDED'
  | 'BLOCKER_REPORTED'
  | 'BLOCKER_RESOLVED'
  | 'TEAM_CREATED'
  | 'TEAM_UPDATED'
  | 'MEMBER_ADDED'
  | 'MEMBER_REMOVED'
  | 'USER_CREATED'
  | 'USER_UPDATED';

export interface ProjectActivity {
  id: string;
  projectId: string;
  description: string;
  userId: string | null;
  userName: string;
  timestamp: string;
  type: ActivityType;
}
