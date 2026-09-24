/**
 * Auth API module.
 * Handles login, logout, fetching the current authenticated user,
 * profile updates, and password change.
 */

import { User, LoginCredentials, AuthTokens, UpdateProfilePayload, ChangePasswordPayload } from '@/types';
import { apiClient } from './client';
import { setLoginFlag, clearLoginFlag, hasLoginFlag } from '../auth/storage';

export async function login(credentials: LoginCredentials): Promise<User> {
  await apiClient.post<AuthTokens>('/auth/login', {
    email: credentials.email,
    password: credentials.password,
  });
  setLoginFlag();
  const user = await getCurrentUser();
  if (!user) throw new Error('Failed to fetch user after login');
  return user;
}

export async function logout(): Promise<void> {
  try {
    await apiClient.post('/auth/logout');
  } catch {
    // Ignore errors on logout
  }
  clearLoginFlag();
}

export async function getCurrentUser(): Promise<User | null> {
  if (!hasLoginFlag()) return null;
  try {
    return await apiClient.get<User>('/auth/me');
  } catch {
    clearLoginFlag();
    return null;
  }
}

/**
 * Update the authenticated user's own safe profile fields.
 * Only name, company, and avatarInitials are accepted.
 * Role and account status cannot be modified through this endpoint.
 */
export async function updateProfile(data: UpdateProfilePayload): Promise<User> {
  return apiClient.patch<User>('/auth/me', data);
}

/**
 * Change the authenticated user's password.
 * Requires the current password for verification.
 * Returns 204 No Content on success.
 */
export async function changePassword(data: ChangePasswordPayload): Promise<void> {
  await apiClient.post<void>('/auth/change-password', {
    // Backend expects snake_case; apiClient sends JSON which the backend
    // reads as snake_case (Pydantic default).
    // The toCamelCase transform only applies to responses, not requests.
    current_password: data.currentPassword,
    new_password: data.newPassword,
  });
}

export function isAuthenticated(): boolean {
  return hasLoginFlag();
}
