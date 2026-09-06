/**
 * Reports API module.
 * Report generation and retrieval.
 *
 * In mock mode: returns a placeholder report list.
 * In API mode: communicates with /api/v1/reports endpoints.
 */

import { Report, ReportFilter } from '@/types';
import { apiClient } from './client';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK === 'true';

const MOCK_REPORTS: Report[] = [
  {
    id: 'rpt-1',
    type: 'WEEKLY_WORKFORCE',
    title: 'Weekly Workforce Summary — Week 35, 2026',
    generatedAt: '2026-08-30T09:00:00Z',
    filter: {
      type: 'WEEKLY_WORKFORCE',
      startDate: '2026-08-24',
      endDate: '2026-08-30',
    },
    sections: [
      {
        title: 'Summary',
        content: '284 tasks completed this month across all projects. Backend team leads in output.',
      },
    ],
  },
  {
    id: 'rpt-2',
    type: 'PROJECT_PROGRESS',
    title: 'Project Progress Report — Q3 2026',
    generatedAt: '2026-09-01T09:00:00Z',
    filter: {
      type: 'PROJECT_PROGRESS',
      startDate: '2026-07-01',
      endDate: '2026-09-30',
    },
    sections: [
      {
        title: 'Active Projects',
        content: '12 active projects across 5 teams. 3 at risk or delayed.',
      },
    ],
  },
];

export async function getReports(): Promise<Report[]> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 300));
    return MOCK_REPORTS;
  }
  return apiClient.get<Report[]>('/reports');
}

export async function generateReport(filter: ReportFilter): Promise<Report> {
  if (USE_MOCK) {
    await new Promise(r => setTimeout(r, 800));
    return {
      id: `rpt-${Date.now()}`,
      type: filter.type,
      title: `${filter.type.replace(/_/g, ' ')} Report`,
      generatedAt: new Date().toISOString(),
      filter,
      sections: [
        { title: 'Report generated in mock mode', content: 'Connect to the backend API to generate real reports.' },
      ],
    };
  }
  return apiClient.post<Report>('/reports/generate', filter);
}
