import { apiClient } from './client';
import type { 
  ReportScheduleCreate, 
  ReportScheduleUpdate, 
  ReportScheduleOut, 
  ReportScheduleListItem, 
  ReportRunOut 
} from '@/types';

export const reportSchedulesApi = {
  getReportSchedules: () => 
    apiClient.get<ReportScheduleListItem[]>('/reports/schedules'),
    
  getReportSchedule: (id: string) => 
    apiClient.get<ReportScheduleOut>(`/reports/schedules/${id}`),
    
  createReportSchedule: (payload: ReportScheduleCreate) => 
    apiClient.post<ReportScheduleOut>('/reports/schedules', payload),
    
  updateReportSchedule: (id: string, payload: ReportScheduleUpdate) => 
    apiClient.patch<ReportScheduleOut>(`/reports/schedules/${id}`, payload),
    
  deleteReportSchedule: (id: string) => 
    apiClient.delete<void>(`/reports/schedules/${id}`),
    
  pauseReportSchedule: (id: string) => 
    apiClient.post<ReportScheduleOut>(`/reports/schedules/${id}/pause`),
    
  resumeReportSchedule: (id: string) => 
    apiClient.post<ReportScheduleOut>(`/reports/schedules/${id}/resume`),
    
  getReportRuns: (id: string) => 
    apiClient.get<ReportRunOut[]>(`/reports/schedules/${id}/runs`),
};
