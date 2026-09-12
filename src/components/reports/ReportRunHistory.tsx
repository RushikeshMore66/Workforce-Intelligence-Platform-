'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { reportSchedulesApi } from '@/lib/api/report-schedules';
import { ApiRequestError } from '@/lib/api/client';
import { ReportRunOut } from '@/types';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, RefreshCw, CheckCircle2, Clock, XCircle } from 'lucide-react';

interface ReportRunHistoryProps {
  scheduleId: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ReportRunHistory({ scheduleId, open, onOpenChange }: ReportRunHistoryProps) {
  const [runs, setRuns] = useState<ReportRunOut[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchRuns = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await reportSchedulesApi.getReportRuns(scheduleId);
      setRuns(data);
    } catch (err) {
      if (err instanceof ApiRequestError) {
        setError(err.detail);
      } else {
        setError('An unexpected error occurred while fetching runs.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && scheduleId) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      fetchRuns();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, scheduleId]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100"><CheckCircle2 className="w-3 h-3 mr-1" /> Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100"><XCircle className="w-3 h-3 mr-1" /> Failed</Badge>;
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100"><RefreshCw className="w-3 h-3 mr-1 animate-spin" /> Running</Badge>;
      case 'pending':
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100"><Clock className="w-3 h-3 mr-1" /> Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Run History</DialogTitle>
        </DialogHeader>

        {error && (
          <div className="bg-red-50 text-red-700 border border-red-200 p-3 rounded-md text-sm flex items-start gap-2">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center py-10">
            <RefreshCw className="w-6 h-6 animate-spin text-gray-400" />
          </div>
        ) : (
          <div className="border rounded-md">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Status</TableHead>
                  <TableHead>Started</TableHead>
                  <TableHead>Completed</TableHead>
                  <TableHead>Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} className="text-center py-6 text-gray-500">
                      No report runs yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  runs.map((run) => (
                    <TableRow key={run.id}>
                      <TableCell>{getStatusBadge(run.status)}</TableCell>
                      <TableCell>
                        {run.startedAt ? format(new Date(run.startedAt), 'MMM d, yyyy HH:mm') : '-'}
                      </TableCell>
                      <TableCell>
                        {run.finishedAt ? format(new Date(run.finishedAt), 'MMM d, yyyy HH:mm') : '-'}
                      </TableCell>
                      <TableCell>
                        {run.startedAt && run.finishedAt ? (
                          `${Math.round((new Date(run.finishedAt).getTime() - new Date(run.startedAt).getTime()) / 1000)}s`
                        ) : '-'}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
