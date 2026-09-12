'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { reportSchedulesApi } from '@/lib/api/report-schedules';
import { ApiRequestError } from '@/lib/api/client';
import { ReportScheduleListItem, ReportScheduleOut } from '@/types';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Badge } from '@/components/ui/badge';
import { MoreHorizontal, Play, Pause, Edit, Trash, History, RefreshCw, AlertCircle } from 'lucide-react';
import { ReportScheduleDialog } from './ReportScheduleDialog';
import { ReportRunHistory } from './ReportRunHistory';

export function ReportScheduleTable() {
  const [schedules, setSchedules] = useState<ReportScheduleListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<ReportScheduleOut | undefined>();
  
  const [historyOpen, setHistoryOpen] = useState(false);
  const [selectedHistoryId, setSelectedHistoryId] = useState<string>('');
  
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchSchedules = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportSchedulesApi.getReportSchedules();
      setSchedules(data);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError('Failed to fetch scheduled reports.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchSchedules();
  }, []);

  const handlePauseResume = async (id: string, isActive: boolean) => {
    if (actionLoading) return;
    
    // Check if the application uses confirmation dialogs - implementing a simple window.confirm per plan
    if (isActive) {
      if (!window.confirm('Are you sure you want to pause this schedule?')) return;
    }

    setActionLoading(id);
    try {
      if (isActive) {
        await reportSchedulesApi.pauseReportSchedule(id);
      } else {
        await reportSchedulesApi.resumeReportSchedule(id);
      }
      await fetchSchedules();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        alert(`Error: ${err.detail}`);
      } else {
        alert('An unexpected error occurred.');
      }
    } finally {
      setActionLoading(null);
    }
  };

  const handleDelete = async (id: string) => {
    if (actionLoading) return;
    if (!window.confirm('Are you sure you want to delete this schedule? This removes its configuration permanently.')) return;
    
    setActionLoading(id);
    try {
      await reportSchedulesApi.deleteReportSchedule(id);
      await fetchSchedules();
    } catch (err) {
      if (err instanceof ApiRequestError) {
        alert(`Error: ${err.detail}`);
      } else {
        alert('An unexpected error occurred during deletion.');
      }
    } finally {
      setActionLoading(null);
    }
  };

  const openEdit = (schedule: ReportScheduleListItem) => {
    setEditingSchedule(schedule as ReportScheduleOut); // For simple forms, this cast is often sufficient, ideally would fetch full if needed but fields match
    setDialogOpen(true);
  };

  const openCreate = () => {
    setEditingSchedule(undefined);
    setDialogOpen(true);
  };

  const openHistory = (id: string) => {
    setSelectedHistoryId(id);
    setHistoryOpen(true);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-base font-semibold text-[#172033]">Scheduled Reports</h2>
        <Button onClick={openCreate} className="bg-[#263B80] hover:bg-[#1E2E66] text-white">
          Create Schedule
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 p-3 rounded-md text-sm flex items-start justify-between">
          <div className="flex gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p>{error}</p>
          </div>
          <Button variant="outline" size="sm" onClick={fetchSchedules} className="h-7 px-2">Retry</Button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-12">
          <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : schedules.length === 0 && !error ? (
        <div className="text-center py-12 border rounded-md bg-gray-50">
          <p className="text-gray-500 mb-2">No scheduled reports yet.</p>
          <p className="text-sm text-gray-400">Create your first scheduled report to automate future reporting.</p>
        </div>
      ) : (
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Format</TableHead>
                <TableHead>Frequency</TableHead>
                <TableHead>Next Run</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[80px]">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {schedules.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">
                    {s.name}
                    {s.scopeId && <span className="block text-xs text-gray-500">Scope: {s.scopeId}</span>}
                  </TableCell>
                  <TableCell className="capitalize">{s.reportType}</TableCell>
                  <TableCell className="uppercase">{s.exportFormat}</TableCell>
                  <TableCell className="capitalize">{s.frequency}</TableCell>
                  <TableCell>
                    {s.nextRunAt ? format(new Date(s.nextRunAt), 'MMM d, yyyy HH:mm') : '-'}
                  </TableCell>
                  <TableCell>
                    {s.isActive ? (
                      <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Active</Badge>
                    ) : (
                      <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">Paused</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0" disabled={actionLoading === s.id}>
                          <span className="sr-only">Open menu</span>
                          {actionLoading === s.id ? (
                            <RefreshCw className="h-4 w-4 animate-spin" />
                          ) : (
                            <MoreHorizontal className="h-4 w-4" />
                          )}
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => openEdit(s)}>
                          <Edit className="mr-2 h-4 w-4" /> Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handlePauseResume(s.id, s.isActive)}>
                          {s.isActive ? (
                            <><Pause className="mr-2 h-4 w-4" /> Pause</>
                          ) : (
                            <><Play className="mr-2 h-4 w-4" /> Resume</>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => openHistory(s.id)}>
                          <History className="mr-2 h-4 w-4" /> Run History
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleDelete(s.id)} className="text-red-600 focus:text-red-600 focus:bg-red-50">
                          <Trash className="mr-2 h-4 w-4" /> Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <ReportScheduleDialog 
        open={dialogOpen} 
        onOpenChange={setDialogOpen} 
        initialData={editingSchedule} 
        onSuccess={fetchSchedules} 
      />
      
      <ReportRunHistory
        scheduleId={selectedHistoryId}
        open={historyOpen}
        onOpenChange={setHistoryOpen}
      />
    </div>
  );
}
