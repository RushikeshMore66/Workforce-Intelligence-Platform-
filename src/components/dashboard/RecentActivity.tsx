'use client';

import { motion } from 'motion/react';
import { ProjectActivity, ActivityType } from '@/types';
import { GlassPanel } from '@/components/ui/glass-panel';
import { slideX, stagger } from '@/lib/motion';
import { timeAgo } from '@/lib/utils';
import { CheckCircle2, AlertTriangle, RefreshCw, UserPlus, Pencil, FolderOpen, GitBranch, User, Users, Activity } from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';
import { getInitials } from '@/lib/utils';

interface Props {
  activities: ProjectActivity[];
}

const TYPE_ICON: Record<ActivityType, { Icon: React.ElementType; color: string }> = {
  TASK_COMPLETED:        { Icon: CheckCircle2, color: 'text-[#12B76A]' },
  TASK_UPDATED:          { Icon: Pencil,       color: 'text-[#263B80]' },
  TASK_CREATED:          { Icon: CheckCircle2, color: 'text-[#263B80]' },
  TASK_ASSIGNED:         { Icon: User,         color: 'text-[#B08A3E]' },
  TASK_STATUS_CHANGED:   { Icon: GitBranch,    color: 'text-[#667085]' },
  BLOCKER_REPORTED:      { Icon: AlertTriangle,color: 'text-[#F04438]' },
  BLOCKER_RESOLVED:      { Icon: CheckCircle2, color: 'text-[#12B76A]' },
  PROJECT_CREATED:       { Icon: FolderOpen,   color: 'text-[#263B80]' },
  PROJECT_UPDATED:       { Icon: RefreshCw,    color: 'text-[#667085]' },
  PROJECT_STATUS_CHANGED:{ Icon: Activity,     color: 'text-[#B54708]' },
  PROJECT_ASSIGNED:      { Icon: UserPlus,     color: 'text-[#B08A3E]' },
  WORK_UPDATE_ADDED:     { Icon: Pencil,       color: 'text-[#263B80]' },
  TEAM_CREATED:          { Icon: Users,        color: 'text-[#263B80]' },
  TEAM_UPDATED:          { Icon: Users,        color: 'text-[#667085]' },
  MEMBER_ADDED:          { Icon: UserPlus,     color: 'text-[#B08A3E]' },
  MEMBER_REMOVED:        { Icon: User,         color: 'text-[#F04438]' },
  USER_CREATED:          { Icon: User,         color: 'text-[#263B80]' },
  USER_UPDATED:          { Icon: User,         color: 'text-[#667085]' },
};

export function RecentActivity({ activities }: Props) {
  return (
    <GlassPanel title="Recent Activity" subtitle="Latest changes across your projects" bodyClassName="px-6 pb-5 pt-1">
      {activities.length === 0 ? (
        <p className="py-6 text-sm text-[#667085] text-center">No recent activity.</p>
      ) : (
        <motion.ol variants={stagger(0.05, 0.1)} initial="hidden" whileInView="show" viewport={{ once: true }} className="relative space-y-1">
          <span className="absolute left-[15px] top-3 bottom-3 w-px bg-gradient-to-b from-[#E7E8EC] via-[#E7E8EC] to-transparent" aria-hidden />
          {activities.map(act => {
            const { Icon, color } = TYPE_ICON[act.type] ?? { Icon: Activity, color: 'text-[#667085]' };
            return (
              <motion.li key={act.id} variants={slideX} className="relative flex items-start gap-3 rounded-2xl px-1 py-2.5 hover:bg-white/70 transition-colors">
                <span className={`relative z-10 w-[30px] h-[30px] rounded-full glass-tile flex items-center justify-center flex-shrink-0 ${color}`}>
                  <Icon className="w-3.5 h-3.5" />
                </span>
                <div className="flex-1 min-w-0 pt-0.5">
                  <p className="text-sm text-[#172033] leading-snug">{act.description}</p>
                  <div className="flex items-center gap-2 mt-1 text-[11px] text-[#9CA3AF]">
                    <Avatar initials={getInitials(act.userName)} name={act.userName} size="xs" className="!w-4 !h-4 !text-[8px]" />
                    <span>{act.userName}</span><span>·</span><span>{timeAgo(act.timestamp)}</span>
                  </div>
                </div>
              </motion.li>
            );
          })}
        </motion.ol>
      )}
    </GlassPanel>
  );
}
