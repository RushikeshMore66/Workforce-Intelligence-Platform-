import {
  ChangePasswordPayload,
  LoginCredentials,
  UpdateProfilePayload,
  User,
} from '@/types';

import {
  setLoginFlag,
  clearLoginFlag,
  hasLoginFlag,
} from '@/lib/auth/storage';

import { apiClient } from './client';


interface LoginResponse {
  authenticated: boolean;
  expiresIn: number;
}


interface CsrfResponse {
  csrfEnabled: boolean;
}


export async function ensureCsrfToken(): Promise<void> {
  await apiClient.get<CsrfResponse>(
    '/auth/csrf',
  );
}


export async function login(
  credentials: LoginCredentials,
): Promise<User> {
  await apiClient.post<LoginResponse>(
    '/auth/login',
    {
      email: credentials.email,
      password: credentials.password,
    },
  );

  setLoginFlag();

  await ensureCsrfToken();

  const user = await getCurrentUser();

  if (!user) {
    clearLoginFlag();

    throw new Error(
      'Failed to fetch authenticated user after login',
    );
  }

  return user;
}


export async function logout(): Promise<void> {
  try {
    await apiClient.post(
      '/auth/logout',
    );
  } finally {
    clearLoginFlag();
  }
}


export async function getCurrentUser(): Promise<User | null> {
  if (!hasLoginFlag()) {
    return null;
  }

  try {
    const user = await apiClient.get<User>(
      '/auth/me',
    );

    /*
     * Ensures older sessions created before the CSRF
     * rollout receive a fresh CSRF cookie.
     */
    await ensureCsrfToken();

    return user;
  } catch {
    clearLoginFlag();
    return null;
  }
}


export async function updateProfile(
  data: UpdateProfilePayload,
): Promise<User> {
  return apiClient.patch<User>(
    '/auth/me',
    data,
  );
}


export async function changePassword(
  data: ChangePasswordPayload,
): Promise<void> {
  await apiClient.post<void>(
    '/auth/change-password',
    {
      current_password: data.currentPassword,
      new_password: data.newPassword,
    },
  );
}


export function isAuthenticated(): boolean {
  return hasLoginFlag();
}
