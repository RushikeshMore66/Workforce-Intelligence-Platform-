 
import { useState, useEffect, useCallback } from 'react';
import { TeamViewModel, WorkerViewModel } from '@/types';
import { getTeamById, getTeamWorkers } from '@/lib/api/teams';
import { isApiError } from '@/lib/api/client';

export type TeamDetailState = {
  team: TeamViewModel | null;
  workers: WorkerViewModel[];
  isLoading: boolean;
  error: Error | null;
  statusCode: number | null;
};

export function useTeamDetail(id: string) {
  const [state, setState] = useState<TeamDetailState>({
    team: null,
    workers: [],
    isLoading: true,
    error: null,
    statusCode: null,
  });

  const fetchTeamAndWorkers = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null, statusCode: null }));
    try {
      const [teamData, workersData] = await Promise.all([
        getTeamById(id),
        getTeamWorkers(id),
      ]);
      
      if (!teamData) {
        // mock mode sometimes returns null instead of throwing 404
        setState({ team: null, workers: [], isLoading: false, error: new Error('Not found'), statusCode: 404 });
        return;
      }

      setState({
        team: teamData,
        workers: workersData,
        isLoading: false,
        error: null,
        statusCode: 200,
      });
    } catch (err) {
      const status = isApiError(err) ? err.status : 500;
      setState(prev => ({ ...prev, isLoading: false, error: err as Error, statusCode: status }));
    }
  }, [id]);

  useEffect(() => {
    fetchTeamAndWorkers();
  }, [fetchTeamAndWorkers]);

  return { ...state, refetch: fetchTeamAndWorkers };
}
