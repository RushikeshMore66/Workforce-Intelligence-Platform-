/**
 * Auth module — compatibility shim.
 *
 * This file is a transitional bridge while the full AuthProvider (Phase 4) is
 * being built. Components should migrate from `currentUser` to `useAuth()` as
 * the auth system is implemented.
 *
 * DO NOT add new imports of `currentUser` or `MOCK_CURRENT_USER`.
 * Use `useAuth()` from the auth context instead.
 *
 * @deprecated Import from '@/lib/auth/useAuth' once AuthProvider is wired.
 */

import { User } from '@/types';

/**
 * Hardcoded mock user for development.
 * Will be replaced by the real authenticated user from JWT.
 *
 * @deprecated Use useAuth().user instead.
 */
export const MOCK_CURRENT_USER: User = {
  id: 'owner-1',
  name: 'Rajesh Mehta',
  email: 'rajesh.mehta@apexsoftware.in',
  role: 'OWNER',
  company: 'Apex Software Solutions',
  avatarInitials: 'RM',
};

/**
 * @deprecated Use MOCK_CURRENT_USER or useAuth().user.
 */
export const currentUser = MOCK_CURRENT_USER;
