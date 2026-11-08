'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { motion } from 'motion/react';
import {
  LayoutDashboard, FolderKanban, Users, UsersRound, Briefcase,
  BarChart3, FileText, Lightbulb, Bell, Settings, Building2,
  ChevronLeft, ChevronRight, Shield,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth/useAuth';
import { canAccessSection } from '@/lib/auth/rbac';
import { Avatar } from '@/components/ui/avatar';
import { spring } from '@/lib/motion';

export const NAV_GROUPS = [
  { label: 'Overview', items: [{ label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard }] },
  {
    label: 'Management',
    items: [
      { label: 'Projects', href: '/projects', icon: FolderKanban },
      { label: 'Supervisors', href: '/supervisors', icon: Briefcase },
      { label: 'Teams', href: '/teams', icon: UsersRound },
      { label: 'Workforce', href: '/workforce', icon: Users },
    ],
  },
  {
    label: 'Insights',
    items: [
      { label: 'Analytics', href: '/analytics', icon: BarChart3 },
      { label: 'Reports', href: '/reports', icon: FileText },
      { label: 'Intelligence', href: '/intelligence', icon: Lightbulb },
    ],
  },
  {
    label: 'System',
    items: [
      { label: 'Notifications', href: '/notifications', icon: Bell },
      { label: 'Settings', href: '/settings', icon: Settings },
    ],
  },
  { label: 'Admin', items: [{ label: 'User Management', href: '/admin', icon: Shield }] },
];

interface SidebarProps {
  onMobileClose?: () => void;
  /** Force the expanded layout (used by the mobile drawer). */
  alwaysExpanded?: boolean;
}

export function Sidebar({ onMobileClose, alwaysExpanded }: SidebarProps) {
  const pathname = usePathname();
  const [collapsedState, setCollapsed] = useState(false);
  const collapsed = alwaysExpanded ? false : collapsedState;
  const { user: currentUser } = useAuth();

  const isActive = (href: string) => (href === '/dashboard' ? pathname === '/dashboard' : pathname.startsWith(href));

  return (
    <motion.aside
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0, width: alwaysExpanded ? 264 : collapsed ? 72 : 232 }}
      transition={{ ...spring, opacity: { duration: 0.4 } }}
      className="glass flex flex-col h-full rounded-[24px] flex-shrink-0 overflow-hidden"
    >
      {/* Logo */}
      <div className={cn('flex items-center h-16 flex-shrink-0', collapsed ? 'justify-center' : 'px-5')}>
        <div className="flex items-center gap-2.5 min-w-0">
          <motion.div
            whileHover={{ rotate: -8, scale: 1.08 }}
            transition={spring}
            className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#3B52A5] to-[#1e2f66] flex items-center justify-center flex-shrink-0 shadow-[0_6px_14px_-4px_rgba(38,59,128,0.6)]"
          >
            <Building2 className="w-4.5 h-4.5 text-white" />
          </motion.div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="text-sm font-bold text-[#172033] tracking-tight leading-none">Workforce</div>
              <div className="text-[10px] text-[#9CA3AF] tracking-[0.18em] uppercase leading-none mt-1">Intelligence</div>
            </div>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2 px-3 space-y-4" aria-label="Primary">
        {NAV_GROUPS.map((group) => {
          const visibleItems = group.items.filter((item) => canAccessSection(currentUser?.role, item.href));
          if (visibleItems.length === 0) return null;
          return (
            <div key={group.label}>
              {!collapsed && (
                <div className="px-3 mb-1.5 text-[10px] font-semibold text-[#9CA3AF] uppercase tracking-[0.14em]">
                  {group.label}
                </div>
              )}
              <div className="space-y-1">
                {visibleItems.map((item) => {
                  const active = isActive(item.href);
                  const Icon = item.icon;
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={onMobileClose}
                      title={collapsed ? item.label : undefined}
                      aria-current={active ? 'page' : undefined}
                      className={cn(
                        'group relative flex items-center gap-3 h-10 rounded-full text-[13px] font-medium transition-colors',
                        collapsed ? 'justify-center' : 'px-3.5',
                        active ? 'text-white' : 'text-[#667085] hover:text-[#172033] hover:bg-white/70'
                      )}
                    >
                      {active && (
                        <motion.span
                          layoutId="nav-active-pill"
                          transition={spring}
                          className="absolute inset-0 rounded-full bg-[#111827] shadow-[0_8px_18px_-8px_rgba(17,24,39,0.7)]"
                        />
                      )}
                      <Icon className="relative w-[17px] h-[17px] flex-shrink-0 transition-transform duration-200 group-hover:scale-110" />
                      {!collapsed && <span className="relative">{item.label}</span>}
                    </Link>
                  );
                })}
              </div>
            </div>
          );
        })}
      </nav>

      {!alwaysExpanded && (
        <div className="px-3 pb-2">
          <button
            onClick={() => setCollapsed(!collapsedState)}
            className="w-full flex items-center justify-center gap-2 h-9 rounded-full text-[#9CA3AF] hover:text-[#172033] hover:bg-white/70 transition-colors text-xs"
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : (<><ChevronLeft className="w-3.5 h-3.5" /><span>Collapse</span></>)}
          </button>
        </div>
      )}

      {currentUser && (
        <div className={cn('m-3 mt-0 rounded-2xl glass-tile p-2.5', collapsed && 'p-2')}>
          <div className={cn('flex items-center gap-2.5', collapsed && 'justify-center')}>
            <Avatar initials={currentUser.avatarInitials} name={currentUser.name} size="sm" />
            {!collapsed && (
              <div className="min-w-0">
                <div className="text-xs font-semibold text-[#172033] truncate">{currentUser.name}</div>
                <div className="text-[10px] text-[#9CA3AF] truncate">{currentUser.company}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </motion.aside>
  );
}
