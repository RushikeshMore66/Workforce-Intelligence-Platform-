/**
 * Centralized HTTP client for the Workforce Intelligence Platform.
 *
 * Usage:
 *   import { apiClient } from '@/lib/api/client';
 *   const projects = await apiClient.get<Project[]>('/projects');
 *
 * All methods automatically:
 *  - Prepend NEXT_PUBLIC_API_URL + /api/v1
 *  - Attach the Authorization header via getAuthHeaders() abstraction
 *  - Transform snake_case response keys to camelCase
 *  - Throw ApiRequestError on non-2xx responses
 *  - Timeout after 10 seconds by default
 */

import { toCamelCase } from './mappers';
import { getStoredToken } from '../auth/storage';

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1`;

// ── Event callbacks ──────────────────────────────────────────

type UnauthorizedCallback = () => void;
let onUnauthorized: UnauthorizedCallback | null = null;

export function setUnauthorizedCallback(callback: UnauthorizedCallback) {
  onUnauthorized = callback;
}

/**
 * Abstraction point for Phase 4 authentication.
 * Services should not know where tokens are stored.
 */
export function getAuthHeaders(): Record<string, string> {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
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

export type RequestParams = Record<string, string | number | boolean | null | undefined>;

interface RequestConfig {
  method: string;
  path: string;
  body?: unknown;
  params?: RequestParams;
  signal?: AbortSignal;
}

async function request<T>({ method, path, body, params, signal }: RequestConfig): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...getAuthHeaders(),
  };

  let url = `${API_BASE}${path}`;

  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });
    const queryString = searchParams.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Set default 10 second timeout if no signal provided
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000);
  const fetchSignal = signal ?? controller.signal;

  let response: Response;
  try {
    response = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
      signal: fetchSignal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiRequestError(408, 'Request timeout exceeded');
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }

  if (response.status === 401) {
    // Notify the auth layer so it can clear state and redirect
    if (onUnauthorized) {
      onUnauthorized();
    }
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
  get: <T>(path: string, params?: RequestParams, signal?: AbortSignal) => 
    request<T>({ method: 'GET', path, params, signal }),
  post: <T>(path: string, body?: unknown, params?: RequestParams, signal?: AbortSignal) => 
    request<T>({ method: 'POST', path, body, params, signal }),
  put: <T>(path: string, body?: unknown, params?: RequestParams, signal?: AbortSignal) => 
    request<T>({ method: 'PUT', path, body, params, signal }),
  patch: <T>(path: string, body?: unknown, params?: RequestParams, signal?: AbortSignal) => 
    request<T>({ method: 'PATCH', path, body, params, signal }),
  delete: <T>(path: string, params?: RequestParams, signal?: AbortSignal) => 
    request<T>({ method: 'DELETE', path, params, signal }),
};

export function isApiError(err: unknown): err is ApiRequestError {
  return err instanceof ApiRequestError;
}
