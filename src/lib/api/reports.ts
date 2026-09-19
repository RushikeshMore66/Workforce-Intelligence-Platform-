/**
 * Reports API module.
 * Report generation and retrieval.
 */

import { Report, ReportFilter } from '@/types';
import { apiClient } from './client';

export async function getReports(): Promise<Report[]> {
  return apiClient.get<Report[]>('/reports');
}

export async function generateReport(filter: ReportFilter): Promise<Report> {
  return apiClient.post<Report>('/reports/generate', filter);
}
