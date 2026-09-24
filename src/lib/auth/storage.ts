/**
 * Authentication Storage (Migrated to HttpOnly Cookies)
 *
 * Security Note:
 * The JWT token is now stored securely in an HttpOnly cookie set by the backend.
 * We no longer store the token in localStorage to prevent XSS exfiltration.
 * We only store a simple boolean flag to allow the frontend to know if a user
 * is likely logged in (for optimistic rendering/routing) before the /auth/me call resolves.
 */

const LOGGED_IN_KEY = 'wi_logged_in_flag';

export function setLoginFlag(): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(LOGGED_IN_KEY, 'true');
  }
}

export function clearLoginFlag(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(LOGGED_IN_KEY);
  }
}

export function hasLoginFlag(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem(LOGGED_IN_KEY) === 'true';
}
