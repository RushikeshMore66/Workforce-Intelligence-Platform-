/**
 * Users Management API module.
 *
 * Owner-only endpoints for managing user accounts and profiles.
 * All endpoints require authentication; OWNER role is enforced at the backend.
 */

import {
  ManagedUser,
  CreateUserPayload,
  UpdateUserPayload,
} from '@/types';
import { apiClient } from './client';

/**
 * List all users in the organisation.
 * Requires OWNER role (enforced by backend).
 */
export async function getUsers(): Promise<ManagedUser[]> {
  return apiClient.get<ManagedUser[]>('/users');
}

/**
 * Get a specific user by ID.
 * Requires OWNER role (enforced by backend).
 */
export async function getUserById(id: string): Promise<ManagedUser> {
  return apiClient.get<ManagedUser>(`/users/${id}`);
}

/**
 * Create a new user with the appropriate role profile.
 * Requires OWNER role (enforced by backend).
 *
 * The backend validates:
 * - Duplicate email (409)
 * - Role cannot be OWNER (403)
 * - WORKER requires worker_profile (400)
 * - Team/leader/supervisor relationships (400)
 * - Password minimum length (422)
 */
export async function createUser(data: CreateUserPayload): Promise<ManagedUser> {
  return apiClient.post<ManagedUser>('/users', data);
}

/**
 * Update allowed fields on a user.
 * Requires OWNER role (enforced by backend).
 */
export async function updateUser(id: string, data: UpdateUserPayload): Promise<ManagedUser> {
  return apiClient.patch<ManagedUser>(`/users/${id}`, data);
}

/**
 * Activate a deactivated user account.
 * Requires OWNER role (enforced by backend).
 */
export async function activateUser(id: string): Promise<ManagedUser> {
  return apiClient.post<ManagedUser>(`/users/${id}/activate`);
}

/**
 * Deactivate an active user account (prevents login).
 * This is NOT deletion — data is preserved.
 * Cannot deactivate yourself.
 * Requires OWNER role (enforced by backend).
 */
export async function deactivateUser(id: string): Promise<ManagedUser> {
  return apiClient.post<ManagedUser>(`/users/${id}/deactivate`);
}
