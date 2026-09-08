import { useState, useEffect, useCallback } from 'react';
import { ProjectDetail, Task, Blocker, ProjectActivity } from '@/types';
import { getProjectById } from '@/lib/api/projects';
import { getTasksByProject } from '@/lib/api/tasks';
import { getBlockersByProject } from '@/lib/api/blockers';
import { getActivitiesByProject } from '@/lib/api/activities';

export type ResourceState<T> = {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  hasFetched: boolean; // to track lazy loading
};

const initialResourceState = { data: null, isLoading: false, error: null, hasFetched: false };

export function useProjectDetail(id: string) {
  const [project, setProject] = useState<ResourceState<ProjectDetail>>({ ...initialResourceState, isLoading: true });
  const [tasks, setTasks] = useState<ResourceState<Task[]>>(initialResourceState);
  const [blockers, setBlockers] = useState<ResourceState<Blocker[]>>(initialResourceState);
  const [activities, setActivities] = useState<ResourceState<ProjectActivity[]>>(initialResourceState);

  const fetchProject = useCallback(async () => {
    setProject(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const p = await getProjectById(id);
      if (!p) throw new Error('NOT_FOUND');
      setProject({ data: p, isLoading: false, error: null, hasFetched: true });
    } catch (err) {
      setProject(prev => ({ ...prev, isLoading: false, error: err as Error }));
    }
  }, [id]);

  const fetchTasks = useCallback(async () => {
    if (tasks.hasFetched && !tasks.error) return; // already fetched successfully
    setTasks(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const t = await getTasksByProject(id);
      setTasks({ data: t, isLoading: false, error: null, hasFetched: true });
    } catch (err) {
      setTasks(prev => ({ ...prev, isLoading: false, error: err as Error }));
    }
  }, [id, tasks.hasFetched, tasks.error]);

  const fetchBlockers = useCallback(async () => {
    if (blockers.hasFetched && !blockers.error) return;
    setBlockers(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const b = await getBlockersByProject(id);
      setBlockers({ data: b, isLoading: false, error: null, hasFetched: true });
    } catch (err) {
      setBlockers(prev => ({ ...prev, isLoading: false, error: err as Error }));
    }
  }, [id, blockers.hasFetched, blockers.error]);

  const fetchActivities = useCallback(async () => {
    if (activities.hasFetched && !activities.error) return;
    setActivities(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const a = await getActivitiesByProject(id);
      setActivities({ data: a, isLoading: false, error: null, hasFetched: true });
    } catch (err) {
      setActivities(prev => ({ ...prev, isLoading: false, error: err as Error }));
    }
  }, [id, activities.hasFetched, activities.error]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  return {
    project,
    tasks,
    blockers,
    activities,
    fetchProject,
    fetchTasks,
    fetchBlockers,
    fetchActivities,
  };
}
