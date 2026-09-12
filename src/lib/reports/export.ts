import { getAuthHeaders, ApiRequestError } from '../api/client';

const API_BASE = `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/v1`;

export type ReportType = 'organization' | 'project' | 'worker' | 'team' | 'activity';
export type ReportFormat = 'csv' | 'xlsx' | 'pdf';

interface DownloadOptions {
  reportType: ReportType;
  scopeId?: string;
  format: ReportFormat;
}

export async function downloadReport({ reportType, scopeId, format }: DownloadOptions): Promise<void> {
  const headers: Record<string, string> = {
    ...getAuthHeaders(),
  };

  let path = `/reports/${reportType}/export`;
  if (reportType === 'project' || reportType === 'worker' || reportType === 'team') {
    if (!scopeId) throw new Error(`scopeId is required for ${reportType} reports`);
    path = `/reports/${reportType}s/${scopeId}/export`;
  }
  
  const url = `${API_BASE}${path}?export_format=${format}`;

  const response = await fetch(url, {
    method: 'GET',
    headers,
  });

  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      throw new ApiRequestError(response.status, 'Unauthorized or forbidden to export this report.');
    }
    let detail = `Failed to export report (HTTP ${response.status})`;
    try {
      const errorBody = await response.json();
      detail = errorBody.detail || detail;
    } catch {
      // Not JSON
    }
    throw new ApiRequestError(response.status, detail);
  }

  const blob = await response.blob();
  
  // Extract filename from Content-Disposition if possible
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = `${reportType}_report.${format}`;
  
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
    if (filenameMatch && filenameMatch[1]) {
      filename = filenameMatch[1];
    } else {
      const filenameStarMatch = contentDisposition.match(/filename\*=UTF-8''([^;]+)/);
      if (filenameStarMatch && filenameStarMatch[1]) {
        filename = decodeURIComponent(filenameStarMatch[1]);
      }
    }
  }

  // Safe filename - remove slashes
  filename = filename.replace(/[\/\\]/g, '');

  const blobUrl = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = blobUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(blobUrl);
}
