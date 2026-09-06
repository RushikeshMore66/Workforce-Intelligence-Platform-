/**
 * Users API module.
 *
 * In mock mode: reads from an empty set or relies on mock auth.
 * In API mode: backend endpoints NOT AVAILABLE yet.
 */

import { User } from '@/types';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

/**
 * @deprecated Backend endpoint GET /users is NOT AVAILABLE yet.
 */
export async function getUsers(): Promise<User[]> {
  if (USE_MOCK) return []; // Mock logic to be added if UI requires it
  throw new Error('Not implemented in backend');
}

/**
 * @deprecated Backend endpoint GET /users/:id is NOT AVAILABLE yet.
 */
export async function getUserById(_id: string): Promise<User | null> {
  if (USE_MOCK) return null; // Mock logic to be added if UI requires it
  throw new Error('Not implemented in backend');
}
