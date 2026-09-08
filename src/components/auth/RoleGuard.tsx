'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth/useAuth';
import { canAccessSection } from '@/lib/auth/rbac';
import { AccessDenied } from './AccessDenied';

interface RoleGuardProps {
  children: React.ReactNode;
}

/**
 * A wrapper to protect routes based on the user's role and the requested path.
 * Renders an AccessDenied (403) UI if the user is not allowed to view the page.
 */
export function RoleGuard({ children }: RoleGuardProps) {
  const { user, isLoading } = useAuth();
  const pathname = usePathname();

  // If auth is still loading, do not render children or access denied yet
  if (isLoading) {
    return null; // The parent ProtectedRoute already handles the loading spinner
  }

  // If user is not authenticated, ProtectedRoute handles redirecting to login.
  // We only care about authenticated users missing authorization here.
  if (user && !canAccessSection(user.role, pathname)) {
    return <AccessDenied />;
  }

  return <>{children}</>;
}
