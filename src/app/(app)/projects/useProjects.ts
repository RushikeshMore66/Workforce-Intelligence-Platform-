/* eslint-disable react-hooks/set-state-in-effect */

import {
  useState,
  useEffect,
  useCallback,
  useRef,
} from 'react';
import { ProjectViewModel, Supervisor } from '@/types';
import {
  getProjects,
  ProjectFilters,
} from '@/lib/api/projects';
import { getSupervisors } from '@/lib/api/supervisors';

export function useProjects(filters: ProjectFilters) {
  const [projects, setProjects] = useState<ProjectViewModel[]>([]);
  const [supervisors, setSupervisors] = useState<Supervisor[]>([]);

  // Only true when we have never successfully loaded projects.
  const [isLoading, setIsLoading] = useState(true);

  // True when refreshing existing data.
  const [isRefreshing, setIsRefreshing] = useState(false);

  const [error, setError] = useState<Error | null>(null);

  /*
   * Prevent an older request from overwriting newer data.
   *
   * Example:
   * request 1 starts
   * request 2 starts
   * request 2 finishes first
   * request 1 finishes later
   *
   * Request 1 must NOT replace the newer result.
   */
  const requestIdRef = useRef(0);

  /*
   * Tracks whether we have ever received valid project data.
   *
   * This is deliberately a ref because this information is only
   * used to decide how the loading UI behaves; it should not itself
   * trigger another render.
   */
  const hasLoadedRef = useRef(false);

  const search = filters.search;
  const status = filters.status;
  const health = filters.health;
  const priority = filters.priority;

  const fetchProjects = useCallback(async () => {
    const requestId = ++requestIdRef.current;

    const isFirstLoad = !hasLoadedRef.current;

    if (isFirstLoad) {
      setIsLoading(true);
    } else {
      /*
       * Keep the existing project table visible during refresh.
       */
      setIsRefreshing(true);
    }

    setError(null);

    try {
      const [projectData, supervisorData] = await Promise.all([
        getProjects({
          search,
          status,
          health,
          priority,
        }),

        /*
         * Supervisor names are supplementary to the table.
         * A supervisor API failure should not destroy the project page.
         */
        getSupervisors().catch(() => [] as Supervisor[]),
      ]);

      /*
       * Ignore stale requests.
       */
      if (requestId !== requestIdRef.current) {
        return;
      }

      setProjects(projectData);
      setSupervisors(supervisorData);

      hasLoadedRef.current = true;
    } catch (err: unknown) {
      /*
       * Ignore errors from stale requests.
       */
      if (requestId !== requestIdRef.current) {
        return;
      }

      setError(
        err instanceof Error
          ? err
          : new Error('Failed to load projects')
      );
    } finally {
      if (requestId !== requestIdRef.current) {
        return;
      }

      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, [search, status, health, priority]);

  useEffect(() => {
    void fetchProjects();
  }, [fetchProjects]);

  return {
    projects,
    supervisors,
    isLoading,
    isRefreshing,
    error,
    refetch: fetchProjects,
  };
}
