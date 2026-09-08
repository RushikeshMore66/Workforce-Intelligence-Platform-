'use client';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useWorkerDetail } from './useWorkerDetail';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Mail, Briefcase, Users, AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { SkeletonTable } from '@/components/ui/skeleton';

export default function WorkerDetailPage() {
  const params = useParams();
  const id = params.id as string;
  
  const { worker, fetchWorker } = useWorkerDetail(id);
  const { data: w, isLoading, error } = worker;

  if (isLoading) {
    return (
      <div className="max-w-[900px] mx-auto space-y-5">
        <SkeletonTable rows={4} cols={1} />
      </div>
    );
  }

  if (error) {
    const errorMsg = error.message.toLowerCase();
    const is403 = errorMsg.includes('403') || errorMsg.includes('forbidden') || errorMsg.includes('unauthorized');
    const is404 = errorMsg.includes('404') || errorMsg.includes('not found');
    const is401 = errorMsg.includes('401') || errorMsg.includes('unauthenticated');

    return (
      <div className="max-w-[900px] mx-auto space-y-5">
        <div className="flex items-center gap-2 text-sm text-[#667085]">
          <Link href="/workforce" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
            <ArrowLeft className="w-3.5 h-3.5" /> Workforce
          </Link>
        </div>
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h3 className="text-base font-semibold text-[#172033]">
            {is404 ? 'Worker not found' : is403 ? 'Access denied' : is401 ? 'Authentication required' : 'Unable to load worker'}
          </h3>
          <p className="text-sm text-[#667085] mt-1 mb-4">
            {is404 ? 'The requested worker profile does not exist.' :
             is403 ? 'You do not have permission to view this worker.' :
             is401 ? 'Please log in again to continue.' :
             'There was a problem communicating with the server.'}
          </p>
          {(!is403 && !is404) && (
            <Button variant="outline" onClick={fetchWorker}>
              <RefreshCw className="w-4 h-4 mr-2" /> Retry
            </Button>
          )}
        </div>
      </div>
    );
  }

  if (!w) return null;

  const statusBadge = {
    ACTIVE:      { variant: 'success' as const, label: 'Active' },
    ON_LEAVE:    { variant: 'warning' as const, label: 'On Leave' },
    UNAVAILABLE: { variant: 'default' as const, label: 'Unavailable' },
  }[w.status];

  return (
    <div className="max-w-[900px] mx-auto space-y-5">
      <div className="flex items-center gap-2 text-sm text-[#667085]">
        <Link href="/workforce" className="hover:text-[#263B80] flex items-center gap-1 transition-colors">
          <ArrowLeft className="w-3.5 h-3.5" /> Workforce
        </Link>
        <span>/</span>
        <span className="text-[#172033] font-medium">{w.name}</span>
      </div>

      {/* Profile Section */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start gap-5">
          <Avatar initials={w.avatarInitials} name={w.name} size="lg" />
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h1 className="text-xl font-bold text-[#172033]">{w.name}</h1>
              <Badge variant={statusBadge.variant} dot>{statusBadge.label}</Badge>
            </div>
            <div className="flex flex-wrap gap-3 text-sm text-[#667085]">
              <span className="flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5" />{w.role}</span>
              <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" />{w.email}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Organization & Active Project Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Users className="w-3.5 h-3.5" />
            Organization
          </div>
          <div className="space-y-4">
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Team ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.teamId ?? '—'}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Team Leader ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.teamLeaderId ?? '—'}
              </div>
            </div>
            <div>
              <div className="text-xs text-[#9CA3AF] mb-1">Supervisor ID</div>
              <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
                {w.supervisorId ?? '—'}
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white border border-[#E7E8EC] rounded-xl p-5 shadow-sm h-fit">
          <div className="text-xs font-semibold text-[#667085] uppercase tracking-wider mb-4 flex items-center gap-1.5">
            <Briefcase className="w-3.5 h-3.5" />
            Current Project
          </div>
          <div>
            <div className="text-xs text-[#9CA3AF] mb-1">Active Project ID</div>
            <div className="text-sm font-mono text-[#172033] bg-[#F9FAFB] p-2 rounded-md border border-[#E7E8EC] truncate">
              {w.activeProjectId ?? '—'}
            </div>
          </div>
        </div>
      </div>

      {/* Intelligence Empty State Placeholder */}
      <div className="bg-[#F9FAFB] border border-dashed border-[#E7E8EC] rounded-xl p-10 text-center">
        <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center mx-auto mb-3 shadow-sm border border-[#E7E8EC]">
          <Briefcase className="w-5 h-5 text-[#9CA3AF]" />
        </div>
        <h3 className="text-sm font-medium text-[#172033]">Worker Intelligence</h3>
        <p className="text-xs text-[#667085] mt-1 max-w-sm mx-auto">
          Work intelligence will appear here when task and activity analytics are available.
        </p>
      </div>
    </div>
  );
}
