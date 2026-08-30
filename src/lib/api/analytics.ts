import { AnalyticsData } from '@/types';
import { ANALYTICS_DATA } from '@/lib/mock-data/analytics';

export async function getAnalyticsData(): Promise<AnalyticsData> {
  await new Promise(r => setTimeout(r, 300));
  return ANALYTICS_DATA;
}
