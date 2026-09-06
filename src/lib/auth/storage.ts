/**
 * Authentication Token Storage
 *
 * This module isolates JWT token storage.
 *
 * Security Note:
 * The current FastAPI backend requires Authorization: Bearer <token>.
 * It does not support secure HttpOnly cookies for session management.
 * Therefore, tokens must be stored in the browser (localStorage) to persist sessions.
 * This is a known XSS risk tradeoff.
 *
 * This storage module isolates this behavior. If the backend later supports
 * HttpOnly cookies, only this module needs to change to remove manual token handling.
 */

const TOKEN_KEY = 'wi_access_token';

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function clearStoredToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function hasStoredToken(): boolean {
  return !!getStoredToken();
}
