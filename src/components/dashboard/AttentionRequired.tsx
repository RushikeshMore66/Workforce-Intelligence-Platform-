import Link from 'next/link';
import { AttentionItem } from '@/types';
import { AlertTriangle, Clock, ShieldAlert, Zap, Eye, ChevronRight } from 'lucide-react';

interface Props {
  items: AttentionItem[];
}

const TYPE_CONFIG = {
  DEADLINE: { icon: Clock,        bg: 'bg-[#FFFAEB]', border: 'border-[#FEDF89]', iconColor: 'text-[#B54708]' },
  BLOCKER:  { icon: ShieldAlert,  bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]' },
  RISK:     { icon: AlertTriangle,bg: 'bg-[#FEF3F2]', border: 'border-[#FECDCA]', iconColor: 'text-[#B42318]' },
  OVERLOAD: { icon: Zap,          bg: 'bg-[#FFFAEB]', border: 'border-[#FEDF89]', iconColor: 'text-[#B54708]' },
  REVIEW:   { icon: Eye,          bg: 'bg-[#EFF8FF]', border: 'border-[#B2DDFF]', iconColor: 'text-[#1849A9]' },
};

const PRIORITY_DOT = {
  HIGH:   'bg-[#F04438]',
  MEDIUM: 'bg-[#F79009]',
  LOW:    'bg-[#12B76A]',
};

export function AttentionRequired({ items }: Props) {
  return (
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <div className="px-5 py-4 border-b border-[#E7E8EC]">
        <h2 className="text-sm font-semibold text-[#172033]">Attention Required</h2>
        <p className="text-xs text-[#667085] mt-0.5">{items.length} items need your review</p>
      </div>
      <div className="divide-y divide-[#F3F4F6]">
        {items.map(item => {
          const cfg = TYPE_CONFIG[item.type];
          const Icon = cfg.icon;
          return (
            <div key={item.id} className="px-5 py-4 flex items-start gap-3 hover:bg-[#F9FAFB] transition-colors">
              <div className={`w-7 h-7 rounded-md flex items-center justify-center flex-shrink-0 border ${cfg.bg} ${cfg.border}`}>
                <Icon className={`w-3.5 h-3.5 ${cfg.iconColor}`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-[#172033] leading-snug">{item.title}</div>
                    <div className="text-xs text-[#667085] mt-0.5 line-clamp-2">{item.description}</div>
                  </div>
                  <span className={`inline-block w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${PRIORITY_DOT[item.priority]}`} />
                </div>
                {item.projectId && (
                  <Link href={`/projects/${item.projectId}`} className="inline-flex items-center gap-1 text-xs text-[#263B80] hover:underline mt-1.5 font-medium">
                    View project <ChevronRight className="w-3 h-3" />
                  </Link>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
