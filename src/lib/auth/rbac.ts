import { UserRole } from '@/types';

export const ROLES = {
  OWNER: 'OWNER',
  SUPERVISOR: 'SUPERVISOR',
  TEAM_LEADER: 'TEAM_LEADER',
  WORKER: 'WORKER',
} as const;

/**
 * Helper to check if a user role is included in a list of allowed roles.
 * 
 * NOTE: Frontend RBAC is for UX purposes only (hiding buttons, redirecting pages).
 * The backend remains the authoritative security boundary.
 */
export function hasRole(userRole: UserRole | string | undefined | null, allowedRoles: UserRole[]): boolean {
  if (!userRole) return false;
  return allowedRoles.includes(userRole as UserRole);
}

// Canonical route-to-role mappings for UX visibility
export const PAGE_PERMISSIONS: Record<string, UserRole[]> = {
  '/dashboard': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER, ROLES.WORKER],
  '/projects': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER, ROLES.WORKER],
  '/supervisors': [ROLES.OWNER],
  '/teams': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER], // WORKER accesses team info elsewhere
  '/workforce': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER, ROLES.WORKER],
  '/analytics': [ROLES.OWNER], 
  '/reports': [ROLES.OWNER],
  '/intelligence': [ROLES.OWNER],
  '/notifications': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER, ROLES.WORKER],
  '/settings': [ROLES.OWNER, ROLES.SUPERVISOR, ROLES.TEAM_LEADER, ROLES.WORKER],
};

/**
 * Checks if a user has access to a specific top-level section based on frontend UX rules.
 */
export function canAccessSection(userRole: UserRole | string | undefined | null, path: string): boolean {
  const topLevel = '/' + path.split('/')[1];
  const allowed = PAGE_PERMISSIONS[topLevel];
  if (!allowed) {
    if (topLevel === '/' || topLevel === '/login') return true;
    return false;
  }
  return hasRole(userRole, allowed);
}
