'use client';

import { useState } from 'react';
import { Download, AlertCircle, RefreshCw, FileText, Lock } from 'lucide-react';
import { downloadReport, ReportType, ReportFormat } from '@/lib/reports/export';
import { ApiRequestError } from '@/lib/api/client';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuth } from '@/lib/auth/useAuth';
import { ROLES } from '@/lib/auth/rbac';
import { ReportScheduleTable } from '@/components/reports/ReportScheduleTable';

export default function ReportsPage() {
  const { user } = useAuth();
  
  const [reportType, setReportType] = useState<ReportType>('organization');
  const [scopeId, setScopeId] = useState('');
  const [format, setFormat] = useState<ReportFormat>('csv');
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const isScopeRequired = ['project', 'worker', 'team'].includes(reportType);
  const canExport = !exporting && (!isScopeRequired || scopeId.trim().length > 0);

  const handleExport = async () => {
    if (!canExport) return;
    
    setExporting(true);
    setError(null);
    setSuccess(false);
    
    try {
      await downloadReport({
        reportType,
        scopeId: isScopeRequired ? scopeId.trim() : undefined,
        format,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred while downloading the report.');
      }
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="max-w-[1000px] mx-auto space-y-5 pb-10">
      <div>
        <h1 className="wi-page-title">Reports</h1>
        <p className="text-sm text-[#667085] mt-0.5">Generate, download, and schedule comprehensive data reports.</p>
      </div>

      <Tabs defaultValue="export" className="w-full">
        <TabsList className="mb-6 bg-white border border-gray-200">
          <TabsTrigger value="export">Export Reports</TabsTrigger>
          <TabsTrigger value="scheduled">Scheduled Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="export" className="focus:outline-none">
          <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-[#172033] mb-5">Configure Report</h2>
            
            <div className="space-y-5">
              {/* Report Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
                <select
                  value={reportType}
                  onChange={(e) => {
                    setReportType(e.target.value as ReportType);
                    setScopeId('');
                    setError(null);
                    setSuccess(false);
                  }}
                  className="w-full sm:w-1/2 bg-white border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                >
                  <option value="organization">Organization Analytics</option>
                  <option value="project">Project Analytics</option>
                  <option value="worker">Worker Analytics</option>
                  <option value="team">Team Analytics</option>
                  <option value="activity">Activity Log</option>
                </select>
              </div>

              {/* Scope ID */}
              {isScopeRequired && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {reportType.charAt(0).toUpperCase() + reportType.slice(1)} ID <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={scopeId}
                    onChange={(e) => setScopeId(e.target.value)}
                    placeholder={`Enter ${reportType} ID`}
                    className="w-full sm:w-1/2 bg-white border border-gray-300 rounded-md p-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">Required to generate a specific {reportType} report.</p>
                </div>
              )}

              {/* Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Format</label>
                <div className="flex gap-3">
                  {(['csv', 'xlsx', 'pdf'] as ReportFormat[]).map((fmt) => (
                    <label key={fmt} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="format"
                        value={fmt}
                        checked={format === fmt}
                        onChange={(e) => setFormat(e.target.value as ReportFormat)}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700 uppercase">{fmt}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-100 flex items-center gap-4">
              <Button 
                onClick={handleExport} 
                disabled={!canExport}
                className="flex items-center gap-2 bg-[#263B80] hover:bg-[#1E2E66] text-white disabled:opacity-50"
              >
                {exporting ? (
                  <><RefreshCw className="w-4 h-4 animate-spin" /> Preparing report...</>
                ) : (
                  <><Download className="w-4 h-4" /> Export Report</>
                )}
              </Button>
              
              {success && (
                <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                  <FileText className="w-4 h-4" /> Export complete
                </span>
              )}
            </div>
            
            {error && (
              <div className="mt-4 bg-red-50 text-red-700 border border-red-200 p-3 rounded-md text-sm flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}
          </div>
        </TabsContent>
        
        <TabsContent value="scheduled" className="focus:outline-none">
          <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
            {user?.role === ROLES.OWNER ? (
              <ReportScheduleTable />
            ) : (
              <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
                <div className="w-12 h-12 rounded-full bg-red-50 flex items-center justify-center mb-4">
                  <Lock className="w-6 h-6 text-red-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Access Denied</h3>
                <p className="text-gray-500 max-w-md">
                  You do not have permission to access scheduled reports. Only Organization Owners can configure schedule automation.
                </p>
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
