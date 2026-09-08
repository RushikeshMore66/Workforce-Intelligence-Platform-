import { useState, useEffect, useCallback } from 'react';
import { WorkerViewModel } from '@/types';
import { getWorkerById } from '@/lib/api/workers';

export type ResourceState<T> = {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  hasFetched: boolean;
};

const initialResourceState = { data: null, isLoading: false, error: null, hasFetched: false };

export function useWorkerDetail(id: string) {
  const [worker, setWorker] = useState<ResourceState<WorkerViewModel>>({ ...initialResourceState, isLoading: true });

  const fetchWorker = useCallback(async () => {
    setWorker(prev => ({ ...prev, isLoading: true, error: null }));
    try {
      const w = await getWorkerById(id);
      if (!w) throw new Error('NOT_FOUND');
      setWorker({ data: w, isLoading: false, error: null, hasFetched: true });
    } catch (err) {
      setWorker(prev => ({ ...prev, isLoading: false, error: err as Error }));
    }
  }, [id]);

  // eslint-disable-next-line react-hooks/set-state-in-effect
  useEffect(() => {
    fetchWorker();
  }, [fetchWorker]);

  return {
    worker,
    fetchWorker,
  };
}
