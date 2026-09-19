/**
 * Auth API module.
 * Handles login, logout, and fetching the current authenticated user.
 */

import { User, LoginCredentials, AuthTokens } from '@/types';
import { apiClient } from './client';
import { setStoredToken, clearStoredToken, getStoredToken } from '../auth/storage';

export async function login(credentials: LoginCredentials): Promise<User> {
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
}

export async function getCurrentUser(): Promise<User | null> {
  const token = getStoredToken();
  if (!token) return null;
  try {
    return await apiClient.get<User>('/auth/me');
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return !!getStoredToken();
}
