import { Notification } from '@/types';
import { mockNotificationsRepo } from './mock/notifications-repository';

export async function getNotifications(): Promise<Notification[]> {
  return mockNotificationsRepo.getAll();
}

export async function getUnreadCount(): Promise<number> {
  return mockNotificationsRepo.getUnreadCount();
}

export async function markNotificationRead(id: string): Promise<void> {
  return mockNotificationsRepo.markAsRead(id);
}

export async function markAllNotificationsRead(): Promise<void> {
  return mockNotificationsRepo.markAllAsRead();
}
