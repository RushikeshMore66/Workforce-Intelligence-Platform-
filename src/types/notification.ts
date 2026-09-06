export type NotificationType =
  | 'PROJECT_ALERT'
  | 'BLOCKER'
  | 'DEADLINE'
  | 'TASK'
  | 'WORK_UPDATE'
  | 'TEAM_UPDATE'
  | 'SYSTEM';

export type NotificationPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  description: string;
  projectId?: string | null;
  read: boolean;
  timestamp: string;
  priority: NotificationPriority;
}
