'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth/useAuth';
import { ApiRequestError } from '@/lib/api/client';

function LoginForm() {
  const { login, isAuthenticated } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get('next');

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      // Validate return URL to prevent open redirects
      const safeReturnUrl = (returnUrl && returnUrl.startsWith('/')) ? returnUrl : '/dashboard';
      router.replace(safeReturnUrl);
    }
  }, [isAuthenticated, router, returnUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await login({ email, password });
      // Redirect handled by useEffect when isAuthenticated becomes true
    } catch (err: unknown) {
      if (err instanceof ApiRequestError) {
        setError(err.detail || 'Authentication failed. Please check your credentials.');
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="bg-[#FEF3F2] border border-[#FEE4E2] p-4 rounded-lg flex items-start gap-3">
          <svg className="w-5 h-5 text-[#F04438] flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p className="text-sm text-[#B42318]">{error}</p>
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-[#344054] mb-1.5">
          Email address
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="block w-full px-4 py-2.5 bg-white border border-[#D0D5DD] rounded-lg text-[#101828] placeholder-[#98A2B3] focus:ring-2 focus:ring-[#263B80]/20 focus:border-[#263B80] transition-colors outline-none"
          placeholder="you@company.com"
        />
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-[#344054] mb-1.5">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="block w-full px-4 py-2.5 bg-white border border-[#D0D5DD] rounded-lg text-[#101828] placeholder-[#98A2B3] focus:ring-2 focus:ring-[#263B80]/20 focus:border-[#263B80] transition-colors outline-none"
          placeholder="••••••••"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[#263B80] hover:bg-[#1E2E65] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#263B80] transition-colors disabled:opacity-70 disabled:cursor-not-allowed"
      >
        {isSubmitting ? (
          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        ) : (
          'Sign in'
        )}
      </button>
    </form>
  );
}

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#F7F7F5] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-[#263B80] text-white font-bold text-xl mb-4 shadow-sm">
            WI
          </div>
          <h1 className="text-3xl font-bold text-[#101828] tracking-tight">Welcome back</h1>
          <p className="mt-2 text-sm text-[#667085]">
            Sign in to your Workforce Intelligence account
          </p>
        </div>

        <div className="bg-white py-8 px-4 sm:px-10 rounded-2xl shadow-[0_4px_24px_-8px_rgba(0,0,0,0.1)] border border-[#E7E8EC]">
          <Suspense fallback={<div className="flex justify-center p-4"><div className="w-6 h-6 border-2 border-[#263B80] border-t-transparent rounded-full animate-spin"></div></div>}>
            <LoginForm />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
