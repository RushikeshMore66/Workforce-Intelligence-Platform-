import { Project } from '@/types';
import { Badge } from '@/components/ui/badge';

export function ProjectPriorityBadge({ priority }: { priority: Project['priority'] }) {
  const configs = {
    LOW:      { variant: 'default' as const, label: 'Low' },
    MEDIUM:   { variant: 'info'    as const, label: 'Medium' },
    HIGH:     { variant: 'warning' as const, label: 'High' },
    CRITICAL: { variant: 'danger'  as const, label: 'Critical' },
  };
  const cfg = configs[priority];
  return <Badge variant={cfg.variant}>{cfg.label}</Badge>;
}
