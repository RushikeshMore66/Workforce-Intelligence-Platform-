import { Project } from '@/types';
import { Badge } from '@/components/ui/badge';

export function ProjectStatusBadge({ status }: { status: Project['status'] }) {
  const configs = {
    PLANNED:   { variant: 'info'    as const, label: 'Planned' },
    ACTIVE:    { variant: 'primary' as const, label: 'Active' },
    ON_HOLD:   { variant: 'warning' as const, label: 'On Hold' },
    COMPLETED: { variant: 'success' as const, label: 'Completed' },
    CANCELLED: { variant: 'default' as const, label: 'Cancelled' },
  };
  const cfg = configs[status];
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
}
