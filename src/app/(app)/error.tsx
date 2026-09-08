'use client';

import { useEffect } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Next.js App Router error boundary for all protected app routes.
 *
 * Catches errors thrown by server components (e.g. failed API calls,
 * unhandled 401/403/500 responses) and renders a user-friendly recovery
 * screen without crashing the entire application.
 *
 * Security note: error.message and error.digest are never rendered
 * verbatim to avoid leaking internal stack traces or server details.
 */
export default function AppError({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // Log to console for development debugging — replace with an error
    // tracking service (e.g. Sentry) in production.
    console.error('[AppError boundary]', error);
  }, [error]);

  return (
    <div className="min-h-[60vh] flex items-center justify-center p-8">
      <div className="max-w-md w-full text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#FEF3F2] border border-[#FEE4E2] mb-6">
          <AlertTriangle className="w-8 h-8 text-[#F04438]" />
        </div>

        <h2 className="text-xl font-semibold text-[#101828] mb-2">
          Something went wrong
        </h2>
        <p className="text-sm text-[#667085] mb-8">
          An error occurred while loading this page. This could be a temporary
          network issue or a server problem.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#263B80] text-white text-sm font-medium hover:bg-[#1E2E65] transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Try again
          </button>
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center px-4 py-2.5 rounded-lg border border-[#D0D5DD] text-[#344054] text-sm font-medium hover:bg-[#F9FAFB] transition-colors"
          >
            Go to dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
