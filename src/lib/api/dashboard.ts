import { DashboardMetrics, AttentionItem } from '@/types';
import { mockDashboardRepo } from './mock/dashboard-repository';
import { PROJECT_ACTIVITIES } from '@/lib/mock-data/activities';

export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  return mockDashboardRepo.getMetrics();
}

export async function getAttentionItems(): Promise<AttentionItem[]> {
  return mockDashboardRepo.getAttentionItems();
}

export async function getRecentActivities() {
  return PROJECT_ACTIVITIES.slice(0, 10);
}