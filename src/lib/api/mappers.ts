/**
 * Response mappers — transforms backend snake_case responses to frontend camelCase.
 *
 * The FastAPI backend uses Python's snake_case convention.
 * The frontend uses camelCase throughout.
 * This module is the single place where that transformation happens.
 *
 * Usage:
 *   import { toCamelCase } from '@/lib/api/mappers';
 *   const project = toCamelCase(apiResponse);
 */

// ── Generic deep snake_case → camelCase transformer ──────────

function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase());
}

/**
 * Recursively transforms all object keys from snake_case to camelCase.
 * Handles nested objects and arrays.
 */
export function toCamelCase<T = unknown>(value: unknown): T {
  if (Array.isArray(value)) {
    return value.map(toCamelCase) as unknown as T;
  }

  if (value !== null && typeof value === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
      result[snakeToCamel(key)] = toCamelCase(val);
    }
    return result as T;
  }

  return value as T;
}

/**
 * Transforms a frontend camelCase object to snake_case for sending to the backend.
 */
function camelToSnake(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

export function toSnakeCase<T = unknown>(value: unknown): T {
  if (Array.isArray(value)) {
    return value.map(toSnakeCase) as unknown as T;
  }

  if (value !== null && typeof value === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
      result[camelToSnake(key)] = toSnakeCase(val);
    }
    return result as T;
  }

  return value as T;
}
