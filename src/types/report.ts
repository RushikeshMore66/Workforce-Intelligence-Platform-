export type ReportType =
  | 'WEEKLY_WORKFORCE'
  | 'PROJECT_PROGRESS'
  | 'TEAM_PERFORMANCE'
  | 'BLOCKED_WORK'
  | 'SUPERVISOR_SUMMARY'
  | 'COMPANY_OVERVIEW';

export interface ReportFilter {
  type: ReportType;
  startDate: string;
  endDate: string;
  projectId?: string;
  teamId?: string;
}

export interface Report {
  id: string;
  type: ReportType;
  title: string;
  generatedAt: string;
  filter: ReportFilter;
  sections: ReportSection[];
}

export interface ReportSection {
  title: string;
  content: string;
  data?: Record<string, number | string>[];
}
