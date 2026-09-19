/**
 * Notifications API module.
 */

import { Notification } from '@/types';
import { apiClient } from './client';

export async function getNotifications(): Promise<Notification[]> {
  return apiClient.get<Notification[]>('/notifications');
}

export async function getUnreadCount(): Promise<number> {
  const data = await apiClient.get<{ count: number }>('/notifications/unread-count');
  return data.count;
}

export async function markNotificationRead(id: string): Promise<void> {
  await apiClient.patch(`/notifications/${id}/read`, {});
}

export async function markAllNotificationsRead(): Promise<void> {
  await apiClient.post('/notifications/read-all');
}
