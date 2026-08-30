import { Notification } from '@/types';
import { NOTIFICATIONS } from '@/lib/mock-data/notifications';

const STORAGE_KEY = 'wi_mock_notifications';

function delay(ms = 200) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

class NotificationsRepository {
  private getNotifications(): Notification[] {
    if (typeof window === 'undefined') return NOTIFICATIONS;
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(NOTIFICATIONS));
      return NOTIFICATIONS;
    }
    try {
      return JSON.parse(stored) as Notification[];
    } catch {
      return NOTIFICATIONS;
    }
  }

  private save(notifs: Notification[]) {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(notifs));
    }
  }

  async getAll(): Promise<Notification[]> {
    await delay();
    return this.getNotifications();
  }

  async getUnreadCount(): Promise<number> {
    await delay(100);
    return this.getNotifications().filter(n => !n.read).length;
  }

  async markAsRead(id: string): Promise<void> {
    await delay(150);
    const notifs = this.getNotifications();
    const idx = notifs.findIndex(n => n.id === id);
    if (idx !== -1) {
      notifs[idx] = { ...notifs[idx], read: true };
      this.save(notifs);
    }
  }

  async markAllAsRead(): Promise<void> {
    await delay(200);
    const notifs = this.getNotifications().map(n => ({ ...n, read: true }));
    this.save(notifs);
  }
}

export const mockNotificationsRepo = new NotificationsRepository();
