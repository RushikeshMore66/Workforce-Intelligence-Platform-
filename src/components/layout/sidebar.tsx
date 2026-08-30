'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, FolderKanban, Users, UsersRound, Briefcase,
  BarChart3, FileText, Lightbulb, Bell, Settings, Building2,
  ChevronLeft, ChevronRight,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { currentUser } from '@/lib/auth';
import { Avatar } from '@/components/ui/avatar';
import { useState } from 'react';

const NAV_GROUPS = [
  {
    label: 'Overview',
    items: [
      { label: 'Dashboard',    href: '/dashboard',    icon: LayoutDashboard },
    ],
  },
  {
    label: 'Management',
    items: [
      { label: 'Projects',    href: '/projects',     icon: FolderKanban },
      { label: 'Supervisors', href: '/supervisors',  icon: Briefcase },
      { label: 'Teams',       href: '/teams',        icon: UsersRound },
      { label: 'Workforce',   href: '/workforce',    icon: Users },
    ],
  },
  {
    label: 'Insights',
    items: [
      { label: 'Analytics',   href: '/analytics',   icon: BarChart3 },
      { label: 'Reports',     href: '/reports',     icon: FileText },
      { label: 'Intelligence',href: '/intelligence',icon: Lightbulb },
    ],
  },
  {
    label: 'System',
    items: [
      { label: 'Notifications',href: '/notifications',icon: Bell },
      { label: 'Settings',    href: '/settings',    icon: Settings },
    ],
  },
];

interface SidebarProps {
  onMobileClose?: () => void;
}

export function Sidebar({ onMobileClose }: SidebarProps) {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  return (
    <aside
      className={cn(
        'flex flex-col h-full bg-[#151E38] text-white transition-[width] duration-300 flex-shrink-0',
        collapsed ? 'w-16' : 'w-[220px]'
      )}
    >
      {/* Logo */}
      <div className={cn('flex items-center h-14 border-b border-white/8 flex-shrink-0', collapsed ? 'justify-center px-3' : 'px-5')}>
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="w-7 h-7 rounded-md bg-[#263B80] flex items-center justify-center flex-shrink-0">
            <Building2 className="w-4 h-4 text-white" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="text-sm font-bold text-white tracking-tight leading-none">Workforce</div>
              <div className="text-[10px] text-[#94a3b8] tracking-wider uppercase leading-none mt-0.5">Intelligence</div>
            </div>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-5">
        {NAV_GROUPS.map(group => (
          <div key={group.label}>
            {!collapsed && (
              <div className="px-2 mb-1.5 text-[10px] font-semibold text-[#475569] uppercase tracking-widest">
                {group.label}
              </div>
            )}
            <div className="space-y-0.5">
              {group.items.map(item => {
                const active = isActive(item.href);
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onMobileClose}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      'wi-nav-link',
                      collapsed && 'justify-center px-0 w-full',
                      active && 'wi-nav-link-active'
                    )}
                  >
                    <Icon className="w-4 h-4 flex-shrink-0" />
                    {!collapsed && <span>{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <div className="px-2 pb-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center gap-2 py-1.5 rounded text-[#64748b] hover:text-white hover:bg-white/7 transition-colors text-xs"
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : (
            <>
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>

      {/* User */}
      <div className={cn('border-t border-white/8 px-3 py-3 flex-shrink-0', collapsed && 'px-2')}>
        <div className={cn('flex items-center gap-2.5', collapsed && 'justify-center')}>
          <Avatar initials={currentUser.avatarInitials} name={currentUser.name} size="sm" />
          {!collapsed && (
            <div className="min-w-0">
              <div className="text-xs font-semibold text-white truncate">{currentUser.name}</div>
              <div className="text-[10px] text-[#94a3b8] truncate">{currentUser.company}</div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}