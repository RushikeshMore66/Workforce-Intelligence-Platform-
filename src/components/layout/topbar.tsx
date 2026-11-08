'use client';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import { AnimatePresence, motion } from 'motion/react';
import { Search, Bell, ChevronDown, LogOut, User, Settings, Menu, X } from 'lucide-react';
import { Sidebar } from '@/components/layout/sidebar';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/auth/useAuth';
import { Avatar } from '@/components/ui/avatar';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

// Breadcrumb mapping
const PAGE_TITLES: Record<string, string> = {
  '/dashboard':     'Dashboard',
  '/projects':      'Projects',
  '/supervisors':   'Supervisors',
  '/teams':         'Teams',
  '/workforce':     'Workforce',
  '/analytics':     'Analytics',
  '/reports':       'Reports',
  '/intelligence':  'Intelligence',
  '/notifications': 'Notifications',
  '/settings':      'Settings',
  '/admin':         'User Management',
};

function getPageTitle(pathname: string): string {
  // Exact match first
  if (PAGE_TITLES[pathname]) return PAGE_TITLES[pathname];
  // Match prefix for detail pages
  const segment = '/' + pathname.split('/')[1];
  return PAGE_TITLES[segment] ?? 'Workforce Intelligence';
}

export function Topbar() {
  const pathname = usePathname();
  const pageTitle = getPageTitle(pathname);
  const { user: currentUser, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  // Breadcrumb segments for detail pages
  const segments = pathname.split('/').filter(Boolean);
  const isDetailPage = segments.length >= 2;

  return (
    <motion.header initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }} className="glass h-14 rounded-full flex items-center justify-between pl-3 pr-2.5 md:pl-6 gap-3 flex-shrink-0">
      {/* Left: Title / Breadcrumb */}
      <div className="flex items-center gap-2 min-w-0">
        <button
          onClick={() => setMenuOpen(true)}
          className="md:hidden w-9 h-9 rounded-full glass-pill flex items-center justify-center text-[#172033]"
          aria-label="Open navigation"
        >
          <Menu className="w-4 h-4" />
        </button>
        {isDetailPage ? (
          <nav className="flex items-center gap-1.5 text-sm" aria-label="Breadcrumb">
            <span className="text-[#667085]">{PAGE_TITLES['/' + segments[0]] ?? segments[0]}</span>
            <span className="text-[#D1D5DB]">/</span>
            <span className="text-[#172033] font-medium truncate max-w-[200px]">Detail</span>
          </nav>
        ) : (
          <h1 className="text-base font-semibold text-[#172033]">{pageTitle}</h1>
        )}
      </div>

      {/* Center: Search */}
      <div className="flex-1 max-w-sm hidden md:block">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#9CA3AF]" />
          <input
            type="search"
            placeholder="Search projects, workers, teams..."
            className={cn(
              'w-full h-9 pl-9 pr-3 text-sm rounded-full border border-transparent bg-white/70',
              'focus:outline-none focus:ring-2 focus:ring-[#263B80]/20 focus:bg-white',
              'placeholder:text-[#9CA3AF] transition-colors'
            )}
          />
        </div>
      </div>

      {/* Right: Notifications + User */}
      <div className="flex items-center gap-2">
        <button
          className="relative w-9 h-9 rounded-full glass-pill flex items-center justify-center text-[#667085] hover:text-[#172033] transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#F04438] border-2 border-white" />
        </button>

        {currentUser && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-full pl-1 pr-2.5 py-1 glass-pill hover:bg-white transition-colors">
                <Avatar initials={currentUser.avatarInitials} size="xs" />
                <span className="text-sm font-medium text-[#172033] hidden sm:block">{currentUser.name.split(' ')[0]}</span>
                <ChevronDown className="w-3.5 h-3.5 text-[#9CA3AF] hidden sm:block" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-52">
              <DropdownMenuLabel>
                <div className="font-semibold text-[#172033] text-sm">{currentUser.name}</div>
                <div className="text-xs text-[#667085] font-normal mt-0.5">{currentUser.email}</div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <User className="w-3.5 h-3.5" />
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Settings className="w-3.5 h-3.5" />
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={logout} destructive>
                <LogOut className="w-3.5 h-3.5" />
                Sign out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </div>
      {typeof document !== 'undefined' && createPortal(<AnimatePresence>
        {menuOpen && (
          <motion.div className="fixed inset-0 z-50 md:hidden" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <div className="absolute inset-0 bg-[#172033]/30 backdrop-blur-sm" onClick={() => setMenuOpen(false)} />
            <motion.div
              initial={{ x: -280 }} animate={{ x: 0 }} exit={{ x: -280 }}
              transition={{ type: 'spring', stiffness: 380, damping: 36 }}
              className="absolute left-3 top-3 bottom-3 w-[264px]"
            >
              <Sidebar alwaysExpanded onMobileClose={() => setMenuOpen(false)} />
              <button onClick={() => setMenuOpen(false)} className="absolute top-4 right-3 w-8 h-8 rounded-full glass-pill flex items-center justify-center" aria-label="Close navigation">
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>, document.body)}
    </motion.header>
  );
}