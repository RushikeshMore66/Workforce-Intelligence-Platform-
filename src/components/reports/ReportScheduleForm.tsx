'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { reportSchedulesApi } from '@/lib/api/report-schedules';
import { ApiRequestError } from '@/lib/api/client';
import { ReportTypeEnum, ReportFormatEnum, ReportFrequencyEnum, ReportScheduleCreate, ReportScheduleUpdate, ReportScheduleOut } from '@/types';

interface ReportScheduleFormProps {
  initialData?: ReportScheduleOut;
  onSuccess: () => void;
  onCancel: () => void;
}

export function ReportScheduleForm({ initialData, onSuccess, onCancel }: ReportScheduleFormProps) {
  const [name, setName] = useState(initialData?.name || '');
  const [reportType, setReportType] = useState<ReportTypeEnum>(initialData?.reportType || 'organization');
  const [scopeId, setScopeId] = useState(initialData?.scopeId || '');
  const [format, setFormat] = useState<ReportFormatEnum>(initialData?.exportFormat || 'csv');
  const [frequency, setFrequency] = useState<ReportFrequencyEnum>(initialData?.frequency || 'weekly');
  const [timezone, setTimezone] = useState(initialData?.timezone || Intl.DateTimeFormat().resolvedOptions().timeZone);
  
  // Convert UTC nextRunAt to local for the datetime-local input
  const getInitialNextRunAt = () => {
    if (initialData?.nextRunAt) {
      const date = new Date(initialData.nextRunAt);
      // Format as YYYY-MM-DDThh:mm
      return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    }
    // Default to tomorrow 9 AM
    const tmrw = new Date();
    tmrw.setDate(tmrw.getDate() + 1);
    tmrw.setHours(9, 0, 0, 0);
    return new Date(tmrw.getTime() - tmrw.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  };
  
  const [nextRunAtLocal, setNextRunAtLocal] = useState(getInitialNextRunAt());
  
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isScopeRequired = ['project', 'worker', 'team'].includes(reportType);
  const isValid = name.trim() !== '' && (!isScopeRequired || scopeId.trim() !== '') && nextRunAtLocal !== '';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || saving) return;

    setSaving(true);
    setError(null);

    // Parse the local time and send as ISO UTC
    const dateObj = new Date(nextRunAtLocal);
    const nextRunAtIso = dateObj.toISOString();

    try {
      if (initialData) {
        const updatePayload: ReportScheduleUpdate = {
          name: name.trim(),
          exportFormat: format,
          frequency,
          timezone,
          nextRunAt: nextRunAtIso,
        };
        await reportSchedulesApi.updateReportSchedule(initialData.id, updatePayload);
      } else {
        const createPayload: ReportScheduleCreate = {
          name: name.trim(),
          reportType,
          scopeId: isScopeRequired ? scopeId.trim() : null,
          exportFormat: format,
          frequency,
          timezone,
          nextRunAt: nextRunAtIso,
        };
        await reportSchedulesApi.createReportSchedule(createPayload);
      }
      onSuccess();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred while saving the schedule.');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 p-3 rounded-md text-sm flex items-start gap-2">
          <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Schedule Name <span className="text-red-500">*</span></label>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="E.g., Weekly Team Report"
          required
        />
      </div>

      {!initialData && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Report Type <span className="text-red-500">*</span></label>
          <select
            value={reportType}
            onChange={(e) => {
              setReportType(e.target.value as ReportTypeEnum);
              setScopeId('');
            }}
            className="w-full bg-white border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="organization">Organization Analytics</option>
            <option value="project">Project Analytics</option>
            <option value="worker">Worker Analytics</option>
            <option value="team">Team Analytics</option>
            <option value="activity">Activity Log</option>
          </select>
        </div>
      )}

      {!initialData && isScopeRequired && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {reportType.charAt(0).toUpperCase() + reportType.slice(1)} ID <span className="text-red-500">*</span>
          </label>
          <Input
            value={scopeId}
            onChange={(e) => setScopeId(e.target.value)}
            placeholder={`Enter ${reportType} ID`}
            required
          />
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Format <span className="text-red-500">*</span></label>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as ReportFormatEnum)}
          className="w-full bg-white border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="csv">CSV</option>
          <option value="xlsx">Excel (XLSX)</option>
          <option value="pdf">PDF</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Frequency <span className="text-red-500">*</span></label>
        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value as ReportFrequencyEnum)}
          className="w-full bg-white border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="monthly">Monthly</option>
        </select>
      </div>
      
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Timezone <span className="text-red-500">*</span></label>
        <Input
          list="timezones"
          value={timezone}
          onChange={(e) => setTimezone(e.target.value)}
          placeholder="E.g., America/New_York"
          required
        />
        <datalist id="timezones">
          <option value="UTC" />
          <option value="America/New_York" />
          <option value="America/Chicago" />
          <option value="America/Denver" />
          <option value="America/Los_Angeles" />
          <option value="Europe/London" />
          <option value="Europe/Paris" />
          <option value="Asia/Kolkata" />
          <option value="Asia/Tokyo" />
          <option value="Australia/Sydney" />
        </datalist>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">First Run Date & Time <span className="text-red-500">*</span></label>
        <Input
          type="datetime-local"
          value={nextRunAtLocal}
          onChange={(e) => setNextRunAtLocal(e.target.value)}
          required
        />
      </div>

      <div className="flex justify-end gap-3 mt-6">
        <Button type="button" variant="outline" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" disabled={!isValid || saving} className="bg-[#263B80] hover:bg-[#1E2E66] text-white">
          {saving && <RefreshCw className="w-4 h-4 mr-2 animate-spin" />}
          {initialData ? 'Save Changes' : 'Create Schedule'}
        </Button>
      </div>
    </form>
  );
}
