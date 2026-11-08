import { useState, useEffect, useCallback, useRef } from 'react';
import { DashboardMetrics, AttentionItem, ProjectActivity, ProjectViewModel, Supervisor, TeamViewModel } from '@/types';
import { getDashboardMetrics, getAttentionItems } from '@/lib/api/dashboard';
import { getRecentActivities } from '@/lib/api/activities';
import { getProjects } from '@/lib/api/projects';
import { getSupervisors } from '@/lib/api/supervisors';
import { getTeams } from '@/lib/api/teams';

export type DashboardSectionState<T> = {
  data: T | null;
  isLoading: boolean;
  /** True while a silent background refresh is in flight (data stays visible). */
  isRefreshing: boolean;
  error: Error | null;
};

type LoadMode = 'initial' | 'silent' | 'retry';

const REFRESH_INTERVAL_MS = 60_000;

const initial = <T,>(): DashboardSectionState<T> => ({ data: null, isLoading: true, isRefreshing: false, error: null });

/**
 * Loads one dashboard section. Initial loads show skeletons; later refreshes
 * are silent so polling never flashes the UI. Stale data is kept on refresh failure.
 */
function useSection<T>(fetcher: () => Promise<T>, fallbackOnError?: T) {
  const [state, setState] = useState<DashboardSectionState<T>>(initial<T>());
  const mounted = useRef(true);
  const hasData = useRef(false);

  useEffect(() => {
    mounted.current = true;
    return () => { mounted.current = false; };
  }, []);

  // mode: 'initial' — state already shows loading, nothing to set up front;
  //       'silent'  — background refresh, keep data on screen;
  //       'retry'   — user-triggered, show the loading state again.
  const load = useCallback(async (mode: LoadMode = 'retry') => {
    if (mode !== 'initial') {
      const background = mode === 'silent' && hasData.current;
      setState(prev => ({ ...prev, isLoading: !background, isRefreshing: background, error: null }));
    }
    try {
      const data = await fetcher();
      if (!mounted.current) return;
      hasData.current = true;
      setState({ data, isLoading: false, isRefreshing: false, error: null });
    } catch (error) {
      if (!mounted.current) return;
      if (fallbackOnError !== undefined) {
        hasData.current = true;
        setState({ data: fallbackOnError, isLoading: false, isRefreshing: false, error: null });
        return;
      }
      setState(prev => ({ ...prev, isLoading: false, isRefreshing: false, error: error as Error }));
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetcher]);

  return [state, load] as const;
}

export function useDashboard() {
  const [metrics, loadMetrics] = useSection<DashboardMetrics>(getDashboardMetrics);
  const [attention, loadAttention] = useSection<AttentionItem[]>(getAttentionItems);
  const [activities, loadActivities] = useSection<ProjectActivity[]>(useCallback(() => getRecentActivities(), []));
  const [projects, loadProjects] = useSection<ProjectViewModel[]>(useCallback(() => getProjects(), []));
  // Supervisors and teams enrich the dashboard but are role-gated; a 403 must not break it.
  const [supervisors, loadSupervisors] = useSection<Supervisor[]>(getSupervisors, []);
  const [teams, loadTeams] = useSection<TeamViewModel[]>(getTeams, []);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refreshAll = useCallback(async (mode: LoadMode = 'silent') => {
    await Promise.allSettled([
      loadMetrics(mode), loadAttention(mode), loadActivities(mode),
      loadProjects(mode), loadSupervisors(mode), loadTeams(mode),
    ]);
    setLastUpdated(new Date());
  }, [loadMetrics, loadAttention, loadActivities, loadProjects, loadSupervisors, loadTeams]);

  // Initial load.
  useEffect(() => {
    const t = window.setTimeout(() => { void refreshAll('initial'); }, 0);
    return () => window.clearTimeout(t);
  }, [refreshAll]);

  // Poll while the tab is visible; refresh immediately when it regains focus.
  useEffect(() => {
    const tick = () => { if (document.visibilityState === 'visible') void refreshAll('silent'); };
    const id = window.setInterval(tick, REFRESH_INTERVAL_MS);
    document.addEventListener('visibilitychange', tick);
    return () => { window.clearInterval(id); document.removeEventListener('visibilitychange', tick); };
  }, [refreshAll]);

  const isRefreshing = [metrics, attention, activities, projects].some(s => s.isRefreshing);

  return {
    metrics, attention, activities, projects, supervisors, teams,
    lastUpdated, isRefreshing,
    retryMetrics: () => loadMetrics('retry'),
    retryAttention: () => loadAttention('retry'),
    retryActivities: () => loadActivities('retry'),
    retryProjects: () => loadProjects('retry'),
    retryAll: () => refreshAll('retry'),
  };
}
