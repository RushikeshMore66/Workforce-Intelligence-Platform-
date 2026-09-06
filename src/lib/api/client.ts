/**
 * Centralized HTTP client for the Workforce Intelligence Platform.
 *
 * Usage:
 *   import { apiClient } from '@/lib/api/client';
 *   const projects = await apiClient.get<Project[]>('/projects');
 *
 * All methods automatically:
 *  - Prepend NEXT_PUBLIC_API_URL + /api/v1
 *  - Attach the JWT Bearer token from localStorage
 *  - Transform snake_case response keys to camelCase
 *  - Throw ApiRequestError on non-2xx responses
 */

import { toCamelCase } from './mappers';

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1`;

// ── Token storage ────────────────────────────────────────────

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

// ── Error class ──────────────────────────────────────────────

export class ApiRequestError extends Error {
  constructor(
    public readonly status: number,
    public readonly detail: string,
    public readonly errorCode?: string,
  ) {
    super(detail);
    this.name = 'ApiRequestError';
  }
}

// ── Core fetch wrapper ───────────────────────────────────────

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
): Promise<T> {
  const token = getStoredToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE}${path}`;

  const response = await fetch(url, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (response.status === 401) {
    // Token expired or invalid — clear it so the auth layer can react
    clearStoredToken();
    throw new ApiRequestError(401, 'Unauthorized — please log in again.');
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    let errorCode: string | undefined;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail ?? errorBody.message ?? detail;
      errorCode = errorBody.error;
    } catch {
      // Response body was not JSON
    }
    throw new ApiRequestError(response.status, detail, errorCode);
  }

  // 204 No Content — return empty
  if (response.status === 204) {
    return undefined as unknown as T;
  }

  const json = await response.json();
  // Transform snake_case keys from the backend to camelCase
  return toCamelCase(json) as T;
}

// ── Public API ───────────────────────────────────────────────

export const apiClient = {
  get: <T>(path: string) => request<T>('GET', path),
  post: <T>(path: string, body: unknown) => request<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => request<T>('PUT', path, body),
  patch: <T>(path: string, body: unknown) => request<T>('PATCH', path, body),
  delete: <T>(path: string) => request<T>('DELETE', path),
};
