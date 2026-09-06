/**
 * Analytics API module.
 *
 * In mock mode: returns static ANALYTICS_DATA.
 * In API mode: communicates with /api/v1/analytics endpoints.
 */

import { AnalyticsData } from '@/types';
import { apiClient } from './client';
import { ANALYTICS_DATA } from '@/lib/mock-data/analytics';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

export async function getAnalyticsData(): Promise<AnalyticsData> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return ANALYTICS_DATA;
  }
  return apiClient.get<AnalyticsData>('/analytics');
}
