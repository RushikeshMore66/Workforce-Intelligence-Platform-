/**
 * Dashboard API module.
 * Provides aggregate dashboard metrics and attention items.
 */

import { DashboardMetrics, AttentionItem } from '@/types';
import { apiClient } from './client';

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  return apiClient.get<DashboardMetrics>('/dashboard/metrics');
}

export async function getAttentionItems(): Promise<AttentionItem[]> {
  return apiClient.get<AttentionItem[]>('/dashboard/attention');
}