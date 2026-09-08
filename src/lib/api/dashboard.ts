/**
 * Dashboard API module.
 * Provides aggregate dashboard metrics and attention items.
 *
 * In mock mode: reads from localStorage-backed DashboardRepository.
 * In API mode: communicates with /api/v1/dashboard endpoints.
 */

import { DashboardMetrics, AttentionItem, ProjectActivity } from '@/types';
import { apiClient } from './client';
import { mockDashboardRepo } from './mock/dashboard-repository';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  if (USE_MOCK) return mockDashboardRepo.getMetrics();
  return apiClient.get<DashboardMetrics>('/dashboard/metrics');
}

export async function getAttentionItems(): Promise<AttentionItem[]> {
  if (USE_MOCK) return mockDashboardRepo.getAttentionItems();
  return apiClient.get<AttentionItem[]>('/dashboard/attention');
}

export async function getDashboardActivities(): Promise<ProjectActivity[]> {
  if (USE_MOCK) return []; // Covered by activities mock
  return apiClient.get<ProjectActivity[]>('/dashboard/activities');
}