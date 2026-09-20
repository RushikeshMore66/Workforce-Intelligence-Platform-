/* eslint-disable react-hooks/set-state-in-effect */
'use client';

import { useState, useEffect } from 'react';
import { Lightbulb, TrendingUp, AlertTriangle, Users, RefreshCw } from 'lucide-react';
import Link from 'next/link';
import { getAttentionItems } from '@/lib/api/dashboard';
import { AttentionItem } from '@/types';
import { SkeletonCard } from '@/components/ui/skeleton';

const TYPE_CONFIG: Record<string, { icon: typeof AlertTriangle; bg: string; border: string; iconColor: string }> = {
  RISK:     { icon: AlertTriangle, bg: 'bg-[#FFFAEB]', border: 'border-[#FEDF89]', iconColor: 'text-[#B54708]' },
  DEADLINE: { icon: AlertTriangle, bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]' },
  BLOCKER:  { icon: AlertTriangle, bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]' },
  OVERLOAD: { icon: Users,         bg: 'bg-[#EEF1FA]', border: 'border-[#c7d0f0]', iconColor: 'text-[#263B80]' },
  REVIEW:   { icon: TrendingUp,    bg: 'bg-[#ECFDF3]', border: 'border-[#ABEFC6]', iconColor: 'text-[#027A48]' },
};

const PRIORITY_BADGE: Record<string, string> = {
  HIGH:   'bg-[#FEF3F2] text-[#B42318] border border-[#FECDCA]',
  MEDIUM: 'bg-[#FFFAEB] text-[#B54708] border border-[#FEDF89]',
  LOW:    'bg-[#F3F4F6] text-[#667085] border border-[#E7E8EC]',
};

export default function IntelligencePage() {
  const [items, setItems] = useState<AttentionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAttentionItems();
      setItems(data);
    } catch {
      setError('Failed to load intelligence items. Please retry.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="max-w-[900px] mx-auto space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="wi-page-title">Intelligence</h1>
          <p className="text-sm text-[#667085] mt-0.5">Risk signals and action items derived from real project data.</p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 text-sm bg-white border border-gray-300 px-3 py-1.5 rounded-md hover:bg-gray-50 transition text-gray-700 font-medium shadow-sm"
        >
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      <div className="bg-[#EEF1FA] border border-[#c7d0f0] rounded-xl px-5 py-3.5 flex items-start gap-3">
        <Lightbulb className="w-4 h-4 text-[#263B80] flex-shrink-0 mt-0.5" />
        <p className="text-sm text-[#263B80]">
          <strong>Intelligence Engine:</strong> These items are computed from live project health, blocker status, and deadline data. They update every time you refresh.
        </p>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <SkeletonCard key={i} className="h-[100px]" />)}
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-100 rounded-xl p-8 text-center">
          <AlertTriangle className="w-6 h-6 text-red-400 mx-auto mb-2" />
          <p className="text-sm text-red-600 mb-3">{error}</p>
          <button onClick={load} className="text-sm text-red-600 underline">Try again</button>
        </div>
      ) : items.length === 0 ? (
        <div className="bg-[#ECFDF3] border border-[#ABEFC6] rounded-xl p-10 text-center">
          <TrendingUp className="w-8 h-8 text-[#027A48] mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-[#027A48] mb-1">All clear</h3>
          <p className="text-sm text-[#667085]">No at-risk, delayed, or blocked projects detected at this time.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map(item => {
            const cfg = TYPE_CONFIG[item.type] ?? TYPE_CONFIG.RISK;
            const Icon = cfg.icon;
            return (
              <div key={item.id} className={`border ${cfg.border} rounded-xl p-5 ${cfg.bg}`}>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-white/60 flex items-center justify-center flex-shrink-0">
                    <Icon className={`w-4 h-4 ${cfg.iconColor}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <h3 className="text-sm font-semibold text-[#172033]">{item.title}</h3>
                      <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${PRIORITY_BADGE[item.priority] ?? PRIORITY_BADGE.LOW}`}>
                        {item.priority}
                      </span>
                    </div>
                    <p className="text-sm text-[#374151] leading-relaxed">{item.description}</p>
                    {item.projectId && (
                      <Link href={`/projects/${item.projectId}`} className="inline-flex items-center gap-1.5 text-xs font-medium text-[#263B80] hover:underline mt-3">
                        View Project →
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
