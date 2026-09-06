'use client';
import { usePathname } from 'next/navigation';
import { Search, Bell, ChevronDown, LogOut, User, Settings } from 'lucide-react';
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

  // Breadcrumb segments for detail pages
  const segments = pathname.split('/').filter(Boolean);
  const isDetailPage = segments.length >= 2;

  return (
    <header className="h-14 bg-white border-b border-[#E7E8EC] flex items-center justify-between px-5 gap-4 flex-shrink-0">
      {/* Left: Title / Breadcrumb */}
      <div className="flex items-center gap-2 min-w-0">
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
              'w-full h-8 pl-9 pr-3 text-sm rounded-md border border-[#E7E8EC] bg-[#F7F7F5]',
              'focus:outline-none focus:ring-2 focus:ring-[#263B80]/20 focus:border-[#263B80] focus:bg-white',
              'placeholder:text-[#9CA3AF] transition-colors'
            )}
          />
        </div>
      </div>

      {/* Right: Notifications + User */}
      <div className="flex items-center gap-2">
        <button
          className="relative w-8 h-8 rounded-md flex items-center justify-center text-[#667085] hover:bg-[#F3F4F6] hover:text-[#172033] transition-colors"
          aria-label="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#F04438] border-2 border-white" />
        </button>

        {currentUser && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-[#F3F4F6] transition-colors">
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
    </header>
  );
}