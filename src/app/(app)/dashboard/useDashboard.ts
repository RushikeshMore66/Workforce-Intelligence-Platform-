import { useState, useEffect, useCallback } from 'react';
import { DashboardMetrics, AttentionItem, ProjectActivity, ProjectViewModel } from '@/types';
import { getDashboardMetrics, getAttentionItems } from '@/lib/api/dashboard';
import { getRecentActivities } from '@/lib/api/activities';
import { getProjects } from '@/lib/api/projects';

export type DashboardSectionState<T> = {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
};

export function useDashboard() {
  const [metrics, setMetrics] = useState<DashboardSectionState<DashboardMetrics>>({
    data: null, isLoading: true, error: null
  });
  const [attention, setAttention] = useState<DashboardSectionState<AttentionItem[]>>({
    data: null, isLoading: true, error: null
  });
  const [activities, setActivities] = useState<DashboardSectionState<ProjectActivity[]>>({
    data: null, isLoading: true, error: null
  });
  const [projects, setProjects] = useState<DashboardSectionState<ProjectViewModel[]>>({
    data: null, isLoading: true, error: null
  });

  const fetchMetrics = useCallback(async () => {
    setMetrics(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await getDashboardMetrics();
      setMetrics({ data, isLoading: false, error: null });
    } catch (error) {
      setMetrics(prev => ({ ...prev, isLoading: false, error: error as Error }));
    }
  }, []);

  const fetchAttention = useCallback(async () => {
    setAttention(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await getAttentionItems();
      setAttention({ data, isLoading: false, error: null });
    } catch (error) {
      setAttention(prev => ({ ...prev, isLoading: false, error: error as Error }));
    }
  }, []);

  const fetchActivities = useCallback(async () => {
    setActivities(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await getRecentActivities();
      setActivities({ data, isLoading: false, error: null });
    } catch (error) {
      setActivities(prev => ({ ...prev, isLoading: false, error: error as Error }));
    }
  }, []);

  const fetchProjectsData = useCallback(async () => {
    setProjects(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const data = await getProjects();
      setProjects({ data, isLoading: false, error: null });
    } catch (error) {
      setProjects(prev => ({ ...prev, isLoading: false, error: error as Error }));
    }
  }, []);

  const fetchAll = useCallback(() => {
    fetchMetrics();
    fetchAttention();
    fetchActivities();
    fetchProjectsData();
  }, [fetchMetrics, fetchAttention, fetchActivities, fetchProjectsData]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return {
    metrics,
    attention,
    activities,
    projects,
    retryMetrics: fetchMetrics,
    retryAttention: fetchAttention,
    retryActivities: fetchActivities,
    retryProjects: fetchProjectsData,
    retryAll: fetchAll
  };
}
