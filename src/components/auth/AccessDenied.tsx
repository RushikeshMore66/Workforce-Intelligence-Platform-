'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldAlert } from 'lucide-react';
import { useAuth } from '@/lib/auth/useAuth';

export function AccessDenied() {
  const { user } = useAuth();

  return (
    <div className="flex-1 flex items-center justify-center min-h-[60vh]">
      <div className="max-w-md w-full bg-white border border-[#E7E8EC] rounded-2xl p-8 shadow-sm text-center">
        <div className="mx-auto w-12 h-12 bg-[#FEF3F2] rounded-full flex items-center justify-center mb-5 border border-[#FEE4E2]">
          <ShieldAlert className="w-6 h-6 text-[#D92D20]" />
        </div>
        
        <h2 className="text-xl font-bold text-[#101828] mb-2">Access Denied</h2>
        
        <p className="text-sm text-[#475467] mb-6">
          You are signed in as <strong>{user?.name}</strong> with the role of <span className="font-semibold">{user?.role}</span>. 
          However, you don&apos;t have permission to view this area.
        </p>

        <div className="flex flex-col gap-3">
          <Link
            href="/dashboard"
            className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[#263B80] hover:bg-[#1E2E65] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#263B80] transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
