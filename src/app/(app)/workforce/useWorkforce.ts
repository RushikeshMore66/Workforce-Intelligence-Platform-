import { useState, useEffect, useCallback } from 'react';
import { getWorkers, GetWorkersParams } from '@/lib/api/workers';
import { WorkerViewModel } from '@/types';

export function useWorkforce(params?: GetWorkersParams) {
  const [workers, setWorkers] = useState<WorkerViewModel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // We memoize the params manually to avoid infinite loops if the caller passes an inline object
  const search = params?.search;
  const team_id = params?.team_id;
  const status = params?.status;

  const fetchWorkers = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await getWorkers({ search, team_id, status });
      setWorkers(data);
    } catch (err) {
      console.error('Error fetching workers:', err);
      setError(err instanceof Error ? err : new Error('Failed to fetch workers'));
    } finally {
      setIsLoading(false);
    }
  }, [search, team_id, status]);

   
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    fetchWorkers();
  }, [fetchWorkers]);

  return {
    workers,
    isLoading,
    error,
    refetch: fetchWorkers,
  };
}
