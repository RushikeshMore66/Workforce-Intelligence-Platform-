export type ReportTypeEnum = 'organization' | 'project' | 'worker' | 'team' | 'activity';
export type ReportFormatEnum = 'csv' | 'xlsx' | 'pdf';
export type ReportFrequencyEnum = 'daily' | 'weekly' | 'monthly';
export type ReportRunStatusEnum = 'pending' | 'running' | 'completed' | 'failed';

export interface ReportScheduleBase {
  name: string;
  reportType: ReportTypeEnum;
  scopeId: string | null;
  exportFormat: ReportFormatEnum;
  frequency: ReportFrequencyEnum;
  timezone: string;
  nextRunAt: string;
}

export type ReportScheduleCreate = ReportScheduleBase;

export interface ReportScheduleUpdate {
  name?: string;
  exportFormat?: ReportFormatEnum;
  frequency?: ReportFrequencyEnum;
  timezone?: string;
  nextRunAt?: string;
}

export interface ReportScheduleOut extends ReportScheduleBase {
  id: string;
  isActive: boolean;
  createdByUserId: string | null;
  createdAt: string;
  updatedAt: string;
}

export type ReportScheduleListItem = ReportScheduleOut;

export interface ReportRunOut {
  id: string;
  scheduleId: string;
  status: ReportRunStatusEnum;
  startedAt: string | null;
  finishedAt: string | null;
  errorMessage: string | null;
  retryCount: number;
  outputFilename: string | null;
  createdAt: string;
}
