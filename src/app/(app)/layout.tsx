import { Sidebar } from '@/components/layout/sidebar';
import { Topbar } from '@/components/layout/topbar';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { RoleGuard } from '@/components/auth/RoleGuard';
import { MotionProvider } from '@/components/providers/MotionProvider';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <MotionProvider>
        <div className="flex h-screen overflow-hidden gap-3 p-3">
          {/* Desktop sidebar (mobile uses the drawer inside Topbar) */}
          <div className="hidden md:flex h-full flex-shrink-0">
            <Sidebar />
          </div>

          <div className="flex flex-col flex-1 overflow-hidden min-w-0 gap-3">
            <Topbar />
            <main className="flex-1 overflow-y-auto rounded-[24px] px-1 md:px-2 pb-4">
              <RoleGuard>{children}</RoleGuard>
            </main>
          </div>
        </div>
      </MotionProvider>
    </ProtectedRoute>
  );
}
