'use client';
import { useState, useEffect } from 'react';
import { Notification } from '@/types';
import { getNotifications, markNotificationRead, markAllNotificationsRead } from '@/lib/api/notifications';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { timeAgo } from '@/lib/utils';
import { Bell, ShieldAlert, Calendar, Users, Info, CheckCheck, CheckSquare, Pencil } from 'lucide-react';
import Link from 'next/link';
import { NotificationType } from '@/types';

const TYPE_CONFIG: Record<NotificationType, { Icon: React.ElementType; bg: string; iconColor: string }> = {
  BLOCKER:       { Icon: ShieldAlert,  bg: 'bg-[#FEF3F2]', iconColor: 'text-[#B42318]' },
  PROJECT_ALERT: { Icon: Bell,         bg: 'bg-[#FFFAEB]', iconColor: 'text-[#B54708]' },
  DEADLINE:      { Icon: Calendar,     bg: 'bg-[#EFF8FF]', iconColor: 'text-[#1849A9]' },
  TEAM_UPDATE:   { Icon: Users,        bg: 'bg-[#EEF1FA]', iconColor: 'text-[#263B80]' },
  SYSTEM:        { Icon: Info,         bg: 'bg-[#F3F4F6]', iconColor: 'text-[#667085]' },
  TASK:          { Icon: CheckSquare,  bg: 'bg-[#EEF1FA]', iconColor: 'text-[#263B80]' },
  WORK_UPDATE:   { Icon: Pencil,       bg: 'bg-[#F9FAFB]', iconColor: 'text-[#667085]' },
};

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getNotifications().then(n => { setNotifications(n); setLoading(false); });
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  async function handleMarkRead(id: string) {
    await markNotificationRead(id);
    setNotifications(ns => ns.map(n => n.id === id ? { ...n, read: true } : n));
  }

  async function handleMarkAll() {
    await markAllNotificationsRead();
    setNotifications(ns => ns.map(n => ({ ...n, read: true })));
  }

  return (
    <div className="max-w-[800px] mx-auto space-y-5">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="wi-page-title">Notifications</h1>
          <p className="text-sm text-[#667085] mt-0.5">
            {unreadCount > 0 ? `${unreadCount} unread notifications` : 'All caught up!'}
          </p>
        </div>
        {unreadCount > 0 && (
          <Button variant="secondary" size="sm" onClick={handleMarkAll}>
            <CheckCheck className="w-3.5 h-3.5" />
            Mark all read
          </Button>
        )}
      </div>

      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden divide-y divide-[#F3F4F6]">
        {loading ? (
          <div className="py-16 text-center text-sm text-[#9CA3AF]">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="py-16 text-center text-sm text-[#9CA3AF]">No notifications.</div>
        ) : (
          notifications.map(notif => {
            const cfg = TYPE_CONFIG[notif.type] ?? TYPE_CONFIG.SYSTEM;
            const Icon = cfg.Icon;
            return (
              <div
                key={notif.id}
                className={`flex items-start gap-4 px-5 py-4 hover:bg-[#F9FAFB] transition-colors cursor-pointer ${
                  !notif.read ? 'bg-[#F0F4FF]/40' : ''
                }`}
                onClick={() => !notif.read && handleMarkRead(notif.id)}
              >
                <div className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 ${cfg.bg}`}>
                  <Icon className={`w-4 h-4 ${cfg.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className={`text-sm ${!notif.read ? 'font-semibold text-[#172033]' : 'font-medium text-[#172033]'}`}>
                        {notif.title}
                      </div>
                      <p className="text-xs text-[#667085] mt-0.5 leading-relaxed">{notif.description}</p>
                      <div className="flex flex-wrap items-center gap-3 mt-2">
                        <span className="text-xs text-[#9CA3AF]">{timeAgo(notif.timestamp)}</span>
                        <Badge variant={
                          notif.priority === 'HIGH' ? 'danger' :
                          notif.priority === 'MEDIUM' ? 'warning' : 'default'
                        }>
                          {notif.priority}
                        </Badge>
                        {notif.projectId && (
                          <Link
                            href={`/projects/${notif.projectId}`}
                            onClick={e => e.stopPropagation()}
                            className="text-xs text-[#263B80] hover:underline"
                          >
                            View project →
                          </Link>
                        )}
                      </div>
                    </div>
                    {!notif.read && (
                      <span className="w-2 h-2 rounded-full bg-[#263B80] flex-shrink-0 mt-1.5" />
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
