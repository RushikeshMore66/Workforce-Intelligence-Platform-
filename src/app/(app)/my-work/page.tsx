'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  PauseCircle,
  PlayCircle,
  RefreshCw,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { SkeletonCard, SkeletonTable } from '@/components/ui/skeleton';
import { useAuth } from '@/lib/auth/useAuth';
import { getWorkers } from '@/lib/api/workers';
import { changeTaskStatus } from '@/lib/api/tasks';
import { createWorkUpdate } from '@/lib/api/work-updates';
import { apiClient, isApiError } from '@/lib/api/client';
import { Task, WorkerViewModel } from '@/types';

const STATUS_LABELS: Record<Task['status'], string> = {
  PLANNED: 'Planned',
  IN_PROGRESS: 'In Progress',
  ON_HOLD: 'On Hold',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

function statusVariant(status: Task['status']) {
  if (status === 'COMPLETED') return 'success' as const;
  if (status === 'ON_HOLD') return 'danger' as const;
  if (status === 'IN_PROGRESS') return 'primary' as const;
  return 'default' as const;
}

function actionsFor(task: Task): Task['status'][] {
  if (task.status === 'PLANNED') return ['IN_PROGRESS'];
  if (task.status === 'IN_PROGRESS') return ['COMPLETED', 'ON_HOLD'];
  if (task.status === 'ON_HOLD') return ['IN_PROGRESS'];
  return [];
}

export default function MyWorkPage() {
  const { user } = useAuth();
  const [worker, setWorker] = useState<WorkerViewModel | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [updateText, setUpdateText] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busyTaskId, setBusyTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!user) return;

    setLoading(true);
    setError(null);

    try {
      const workers = await getWorkers();
      const currentWorker = workers.find((item) => item.email === user.email);

      if (!currentWorker) {
        throw new Error('No worker profile is linked to this account.');
      }

      const response = await apiClient.get<{
        items: Task[];
        page: number;
        pageSize: number;
        total: number;
      }>(`/workers/${currentWorker.id}/tasks`, {
        page: 1,
        page_size: 100,
      });

      setWorker(currentWorker);
      setTasks(response.items);
    } catch (err) {
      if (isApiError(err)) setError(err.detail);
      else if (err instanceof Error) setError(err.message);
      else setError('Unable to load your work.');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    load();
  }, [load]);

  const metrics = useMemo(() => ({
    total: tasks.length,
    completed: tasks.filter((task) => task.status === 'COMPLETED').length,
    inProgress: tasks.filter((task) => task.status === 'IN_PROGRESS').length,
    onHold: tasks.filter((task) => task.status === 'ON_HOLD').length,
  }), [tasks]);

  const handleStatusChange = async (task: Task, status: Task['status']) => {
    setBusyTaskId(task.id);
    setError(null);

    try {
      let reason: string | undefined;

      if (status === 'ON_HOLD') {
        reason = window.prompt('Why is this task going on hold?')?.trim() || undefined;
        if (!reason) return;
      }

      const updated = await changeTaskStatus(task.id, { status, reason });
      setTasks((current) =>
        current.map((item) => (item.id === task.id ? updated : item)),
      );
    } catch (err) {
      if (isApiError(err)) setError(err.detail);
      else if (err instanceof Error) setError(err.message);
      else setError('Unable to change task status.');
    } finally {
      setBusyTaskId(null);
    }
  };

  const handleWorkUpdate = async (task: Task) => {
    const description = updateText[task.id]?.trim();
    if (!description) return;

    setBusyTaskId(task.id);
    setError(null);

    try {
      await createWorkUpdate({ taskId: task.id, description });
      setUpdateText((current) => ({ ...current, [task.id]: '' }));
    } catch (err) {
      if (isApiError(err)) setError(err.detail);
      else if (err instanceof Error) setError(err.message);
      else setError('Unable to submit work update.');
    } finally {
      setBusyTaskId(null);
    }
  };

  if (loading) {
    return (
      <div className="max-w-[1200px] mx-auto space-y-5">
        <SkeletonCard className="h-36" />
        <SkeletonTable rows={5} cols={4} />
      </div>
    );
  }

  if (error && !worker) {
    return (
      <div className="max-w-[900px] mx-auto py-12">
        <div className="bg-white border border-[#E7E8EC] rounded-xl p-8 text-center shadow-sm">
          <AlertTriangle className="w-8 h-8 text-[#F04438] mx-auto mb-3" />
          <h1 className="text-base font-semibold text-[#172033]">My Work is unavailable</h1>
          <p className="text-sm text-[#667085] mt-1">{error}</p>
          <Button variant="outline" className="mt-4" onClick={load}>
            <RefreshCw className="w-4 h-4 mr-2" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1200px] mx-auto space-y-5">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-widest text-[#667085] font-semibold">
            Execution workspace
          </p>
          <h1 className="wi-page-title mt-1">My Work</h1>
          <p className="text-sm text-[#667085] mt-1">
            Keep assigned work current so your team has a reliable operational picture.
          </p>
        </div>

        {worker && (
          <div className="text-right">
            <div className="text-sm font-semibold text-[#172033]">{worker.name}</div>
            <div className="text-xs text-[#667085]">{worker.role}</div>
          </div>
        )}
      </div>

      {error && (
        <div className="rounded-lg border border-[#FECDCA] bg-[#FEF3F2] px-4 py-3 text-sm text-[#B42318]">
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Assigned', value: metrics.total, icon: Clock3 },
          { label: 'In Progress', value: metrics.inProgress, icon: PlayCircle },
          { label: 'On Hold', value: metrics.onHold, icon: PauseCircle },
          { label: 'Completed', value: metrics.completed, icon: CheckCircle2 },
        ].map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="bg-white border border-[#E7E8EC] rounded-xl p-4 shadow-sm">
              <Icon className="w-4 h-4 text-[#667085] mb-3" />
              <div className="text-2xl font-bold text-[#172033]">{item.value}</div>
              <div className="text-xs text-[#667085] mt-0.5">{item.label}</div>
            </div>
          );
        })}
      </div>

      <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-[#E7E8EC] flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-[#172033]">Assigned Work</h2>
            <p className="text-xs text-[#667085] mt-0.5">Update execution status as work changes.</p>
          </div>
          <Button variant="outline" size="sm" onClick={load}>
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
          </Button>
        </div>

        {tasks.length === 0 ? (
          <div className="py-14 text-center text-sm text-[#667085]">
            No work is currently assigned to you.
          </div>
        ) : (
          <div className="divide-y divide-[#F3F4F6]">
            {tasks.map((task) => {
              const actions = actionsFor(task);

              return (
                <div key={task.id} className="p-5 space-y-3">
                  <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="text-sm font-semibold text-[#172033]">{task.title}</h3>
                        <Badge variant={statusVariant(task.status)}>
                          {STATUS_LABELS[task.status]}
                        </Badge>
                      </div>

                      {task.description && (
                        <p className="text-sm text-[#667085] mt-1">{task.description}</p>
                      )}

                      <div className="text-xs text-[#9CA3AF] mt-2">
                        Due {new Date(task.dueDate).toLocaleDateString('en-IN')}
                      </div>
                    </div>

                    {actions.length > 0 && (
                      <div className="flex gap-2 flex-wrap">
                        {actions.map((nextStatus) => (
                          <Button
                            key={nextStatus}
                            size="sm"
                            variant={nextStatus === 'COMPLETED' ? 'default' : 'outline'}
                            disabled={busyTaskId === task.id}
                            onClick={() => handleStatusChange(task, nextStatus)}
                          >
                            {nextStatus === 'IN_PROGRESS' && 'Start Work'}
                            {nextStatus === 'COMPLETED' && 'Mark Complete'}
                            {nextStatus === 'ON_HOLD' && 'Put On Hold'}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>

                  {task.status !== 'COMPLETED' && task.status !== 'CANCELLED' && (
                    <div className="flex flex-col sm:flex-row gap-2">
                      <Input
                        value={updateText[task.id] ?? ''}
                        onChange={(event) =>
                          setUpdateText((current) => ({
                            ...current,
                            [task.id]: event.target.value,
                          }))
                        }
                        placeholder="What did you complete, discover, or get blocked by?"
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        disabled={!updateText[task.id]?.trim() || busyTaskId === task.id}
                        onClick={() => handleWorkUpdate(task)}
                      >
                        Add Update
                      </Button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
