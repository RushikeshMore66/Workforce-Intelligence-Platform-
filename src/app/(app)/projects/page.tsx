'use client';
import { useState } from 'react';
import { useAuth } from '@/lib/auth/useAuth';
import { useProjects } from './useProjects';
import { ProjectTable } from '@/components/projects/ProjectTable';
import { CreateProjectDialog } from '@/components/projects/CreateProjectDialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { SkeletonTable } from '@/components/ui/skeleton';
import { Plus, Search, RefreshCw, AlertTriangle } from 'lucide-react';

export default function ProjectsPage() {
  const { user } = useAuth();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [toast, setToast] = useState('');
  
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [healthFilter, setHealthFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  const { projects, supervisors, isLoading, error, refetch } = useProjects({
    search: search || undefined,
    status: statusFilter || undefined,
    health: healthFilter || undefined,
    priority: priorityFilter || undefined,
  });

  const canCreate = user?.role === 'OWNER' || user?.role === 'SUPERVISOR';

  const handleProjectCreated = () => {
    refetch();
    setToast('Project created successfully!');
    setTimeout(() => setToast(''), 3500);
  };

  return (
    <div className="max-w-[1400px] mx-auto space-y-5">
      {/* Toast */}
      {toast && (
        <div className="fixed bottom-5 right-5 z-50 flex items-center gap-2 bg-[#172033] text-white text-sm px-4 py-3 rounded-xl shadow-lg animate-in slide-in-from-bottom-5">
          <span className="w-2 h-2 rounded-full bg-[#12B76A]" />
          {toast}
        </div>
      )}

      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="wi-page-title">Projects</h1>
          <p className="text-sm text-[#667085] mt-0.5">Manage projects, monitor progress, and understand project health.</p>
        </div>
        {canCreate && (
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="w-4 h-4" />
            Create Project
          </Button>
        )}
      </div>

      {/* Filters */}
      <div className="bg-white border border-[#E7E8EC] rounded-xl px-4 py-3.5 flex flex-wrap gap-3 items-center shadow-[0_1px_3px_0_rgba(16,24,40,0.06)]">
        <div className="relative flex-1 min-w-[180px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[#9CA3AF]" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search projects or clients..."
            className="pl-9"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Statuses</SelectItem>
              <SelectItem value="PLANNED">Planned</SelectItem>
              <SelectItem value="ACTIVE">Active</SelectItem>
              <SelectItem value="ON_HOLD">On Hold</SelectItem>
              <SelectItem value="COMPLETED">Completed</SelectItem>
              <SelectItem value="CANCELLED">Cancelled</SelectItem>
            </SelectContent>
          </Select>
          <Select value={healthFilter} onValueChange={setHealthFilter}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="All Health" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Health</SelectItem>
              <SelectItem value="ON_TRACK">On Track</SelectItem>
              <SelectItem value="AT_RISK">At Risk</SelectItem>
              <SelectItem value="DELAYED">Delayed</SelectItem>
            </SelectContent>
          </Select>
          <Select value={priorityFilter} onValueChange={setPriorityFilter}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="All Priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Priority</SelectItem>
              <SelectItem value="LOW">Low</SelectItem>
              <SelectItem value="MEDIUM">Medium</SelectItem>
              <SelectItem value="HIGH">High</SelectItem>
              <SelectItem value="CRITICAL">Critical</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <SkeletonTable rows={6} cols={7} />
      ) : error ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h3 className="text-base font-semibold text-[#172033]">Failed to load projects</h3>
          <p className="text-sm text-[#667085] mt-1 mb-4">There was a problem communicating with the server.</p>
          <Button variant="outline" onClick={refetch}>
            <RefreshCw className="w-4 h-4 mr-2" /> Retry
          </Button>
        </div>
      ) : projects.length === 0 ? (
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-12 text-center shadow-sm">
          <div className="w-12 h-12 bg-[#F9FAFB] rounded-full flex items-center justify-center mx-auto mb-3 border border-[#E7E8EC]">
            <Search className="w-6 h-6 text-[#9CA3AF]" />
          </div>
          <h3 className="text-base font-semibold text-[#172033]">No projects found</h3>
          <p className="text-sm text-[#667085] mt-1 max-w-sm mx-auto">
            {search || statusFilter || healthFilter || priorityFilter
              ? "No projects match your current filters. Try adjusting them."
              : "There are no projects available in your workspace."}
          </p>
        </div>
      ) : (
        <ProjectTable
          projects={projects}
          supervisors={supervisors}
          search={search}
          statusFilter={statusFilter}
          healthFilter={healthFilter}
          priorityFilter={priorityFilter}
        />
      )}

      {isCreateOpen && (
        <CreateProjectDialog
          onClose={() => setIsCreateOpen(false)}
          onProjectCreated={handleProjectCreated}
          supervisors={supervisors}
        />
      )}
    </div>
  );
}
