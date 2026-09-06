/**
 * Notifications API module.
 *
 * In mock mode: reads from localStorage-backed NotificationsRepository.
 * In API mode: communicates with /api/v1/notifications endpoints.
 */

import { Notification } from '@/types';
import { apiClient } from './client';
import { mockNotificationsRepo } from './mock/notifications-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getNotifications(): Promise<Notification[]> {
  if (USE_MOCK) return mockNotificationsRepo.getAll();
  return apiClient.get<Notification[]>('/notifications');
}

export async function getUnreadCount(): Promise<number> {
  if (USE_MOCK) return mockNotificationsRepo.getUnreadCount();
  const data = await apiClient.get<{ count: number }>('/notifications/unread-count');
  return data.count;
}

export async function markNotificationRead(id: string): Promise<void> {
  if (USE_MOCK) return mockNotificationsRepo.markAsRead(id);
  await apiClient.patch(`/notifications/${id}/read`, {});
}

export async function markAllNotificationsRead(): Promise<void> {
  if (USE_MOCK) return mockNotificationsRepo.markAllAsRead();
  await apiClient.patch('/notifications/read-all', {});
}
