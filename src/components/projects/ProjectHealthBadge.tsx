import { Project } from '@/types';
import { Badge } from '@/components/ui/badge';

export function ProjectHealthBadge({ health }: { health: Project['health'] }) {
  const configs = {
    ON_TRACK: { variant: 'success' as const, label: 'On Track', dot: true },
    AT_RISK:  { variant: 'warning' as const, label: 'At Risk',  dot: true },
    DELAYED:  { variant: 'danger'  as const, label: 'Delayed',  dot: true },
  };
  const cfg = configs[health];
  return <Badge variant={cfg.variant} dot={cfg.dot}>{cfg.label}</Badge>;
}
