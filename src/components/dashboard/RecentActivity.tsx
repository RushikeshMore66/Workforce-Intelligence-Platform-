import { ProjectActivity, ActivityType } from '@/types';
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
    <div className="bg-white border border-[#E7E8EC] rounded-xl shadow-[0_1px_3px_0_rgba(16,24,40,0.06)] overflow-hidden">
      <div className="px-5 py-4 border-b border-[#E7E8EC]">
        <h2 className="text-sm font-semibold text-[#172033]">Recent Activity</h2>
      </div>
      <div className="divide-y divide-[#F3F4F6]">
        {activities.map(act => {
          const cfg = TYPE_ICON[act.type] ?? { Icon: Activity, color: 'text-[#667085]' };
          const { Icon, color } = cfg;
          return (
            <div key={act.id} className="flex items-start gap-3 px-5 py-3.5">
              <Avatar
                initials={getInitials(act.userName)}
                name={act.userName}
                size="xs"
                className="mt-0.5"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm text-[#172033] leading-snug">{act.description}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <Icon className={`w-3 h-3 ${color}`} />
                  <span className="text-[11px] text-[#9CA3AF]">{timeAgo(act.timestamp)}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
