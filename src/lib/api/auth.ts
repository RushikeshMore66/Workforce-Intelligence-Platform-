/**
 * Auth API module.
 * Handles login, logout, and fetching the current authenticated user.
 *
 * In mock mode: simulates login with a hardcoded owner user.
 * In API mode: communicates with POST /api/v1/auth/login and GET /api/v1/auth/me.
 */

import { User, LoginCredentials, AuthTokens } from '@/types';
import { apiClient } from './client';
import { setStoredToken, clearStoredToken, getStoredToken } from '../auth/storage';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

// ── Mock implementation ───────────────────────────────────────

const MOCK_USER: User = {
  id: 'owner-1',
  name: 'Rajesh Mehta',
  email: 'rajesh.mehta@apexsoftware.in',
  role: 'OWNER',
  company: 'Apex Software Solutions',
  avatarInitials: 'RM',
};

const MOCK_TOKEN = 'mock_jwt_token_do_not_use_in_production';

// ── Public API ────────────────────────────────────────────────

export async function login(credentials: LoginCredentials): Promise<User> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 500));
    if (
      credentials.email === MOCK_USER.email &&
      credentials.password === 'password'
    ) {
      setStoredToken(MOCK_TOKEN);
      return MOCK_USER;
    }
    throw new Error('Invalid email or password');
  }

  const tokens = await apiClient.post<AuthTokens>('/auth/login', {
    email: credentials.email,
    password: credentials.password,
  });
  setStoredToken(tokens.accessToken);
  const user = await getCurrentUser();
  if (!user) throw new Error('Failed to fetch user after login');
  return user;
}

export async function logout(): Promise<void> {
  clearStoredToken();
  // Backend may have a logout endpoint in future — add here when available
}

export async function getCurrentUser(): Promise<User | null> {
  if (USE_MOCK) {
    const token = getStoredToken();
    if (!token) return null;
    return MOCK_USER;
  }

  try {
    return await apiClient.get<User>('/auth/me');
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!getStoredToken();
}
